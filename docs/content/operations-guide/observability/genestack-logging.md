---
title: "Genestack Logging"
weight: 60
---
## Introduction

Genestack logging is a modern, scalable system that collects, stores, and provides an interface to search and read logs on demand. The storage backend is flexible to fit the needs of your deployment. Whether you are backing up to OpenStack Swift, S3, Ceph, or a file share, Genestack logging can fit into your environment.

Out-of-the-box Genestack logging is comprised of three core technologies:

- **[OpenTelemetry](https://opentelemetry.io/)** - A vendor-neutral, open-source standard for telemetry collection. OpenTelemetry's filelog receiver collects logs from Kubernetes containers and OpenStack services, enriches them with metadata, and forwards them to Loki.
- **[Loki](https://github.com/grafana/loki)** - A log aggregation system designed for Kubernetes that stores logs using label-based indexing in a time-series database. Loki is cost-effective and integrates seamlessly with Grafana for visualization.
- **[Grafana](https://grafana.com/)** - Enables you to query, visualize, alert on, and explore your logs alongside metrics and traces in a unified interface.

These components work together to provide a complete logging solution while remaining modular enough to integrate with existing infrastructure if needed.

## Architecture

### Log Flow Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                      Log Collection & Storage                       │
└─────────────────────────────────────────────────────────────────────┘

Log Sources                Collector              Storage        Query
───────────                ─────────              ───────        ─────

/var/log/pods/  ──────┐
 (K8s containers)     │
                      ├──► OpenTelemetry  ──► Loki      ──► Grafana
/var/log/pods/  ──────┤    (filelog        │   (Index)      (Explore)
 (OpenStack svcs)     │     receiver)      │   (Store)      (Search)
                      │                    │                (Alert)
K8s Events  ──────────┘                    │
                                           │
                                           ▼
                                      S3/Swift/Ceph
                                     (Long-term Storage)
```

### Component Roles

| Component | Role | Key Features |
| --- | --- | --- |
| **OpenTelemetry** | Log collection and processing | Multi-line parsing, metadata enrichment, filtering |
| **Loki** | Log aggregation and indexing | Label-based indexing, cost-effective storage, LogQL |
| **Grafana** | Visualization and querying | Interactive search, dashboards, alerting |
| **S3/Swift** | Long-term storage | Durable object storage, cost-effective retention |

## OpenTelemetry log collection

### Overview

OpenTelemetry replaces traditional log collectors like Fluent Bit with a unified, vendor-neutral approach to telemetry collection. The OpenTelemetry Collector uses the `filelog` receiver to gather logs from Kubernetes and OpenStack services.

### Deployment

OpenTelemetry is deployed as a **DaemonSet** in Kubernetes, ensuring it runs on every node of the cluster. This allows it to:

- Access container logs directly from the host filesystem (`/var/log/pods`)
- Collect logs with minimal latency
- Automatically discover new pods and services
- Enrich logs with Kubernetes metadata

### Log sources

The OpenTelemetry filelog receiver collects logs from:

#### Kubernetes container logs

```yaml
receivers:
  filelog/k8s_containers:
    include:
      - /var/log/pods/*/*/*.log
    exclude:
      - /var/log/pods/*/otel-collector/*.log
    start_at: end
    include_file_path: true
    operators:
      - type: container
        id: container-parser
```

What gets collected:

- All pod logs from `/var/log/pods`
- Automatic CRI (Container Runtime Interface) format parsing
- Pod metadata extraction (namespace, pod name, container name)

#### OpenStack service logs

```yaml
receivers:
  filelog/openstack:
    include:
      - /var/log/pods/*/nova-*/*.log
      - /var/log/pods/*/neutron-*/*.log
      - /var/log/pods/*/keystone-*/*.log
      - /var/log/pods/*/cinder-*/*.log
    multiline:
      line_start_pattern: '^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z stdout [FP] )?\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}'
```

What gets collected:

- OpenStack service logs (Nova, Neutron, Keystone, and others)
- Multi-line log messages (Python stack traces and exceptions)
- Structured log parsing (timestamps, severity, components)

#### Kubernetes events

```yaml
receivers:
  k8sobjects:
    auth_type: serviceAccount
    objects:
      - name: events
        mode: watch
        namespaces: [openstack, kube-system, default]
```

What gets collected:

- Kubernetes events (pod lifecycle, scheduling, errors)
- Real-time event streaming
- Namespace-specific event filtering

### Log processing pipeline

OpenTelemetry processes logs through a series of operators.

#### Container parser

Extracts metadata from the CRI log format:

```text
2026-03-17T10:15:30.123456789Z stdout F Actual log message
                                ^^^^^^ ^
                                stream logtag
```

#### Kubernetes metadata extraction

Adds resource attributes:

- `k8s.namespace.name`
- `k8s.pod.name`
- `k8s.pod.uid`
- `k8s.container.name`
- `k8s.node.name`

#### OpenStack log parsing

Parses standard OpenStack log format:

```text
2024-03-17 12:34:56.789 12345 INFO nova.compute.manager [req-abc-123] Log message
└──────────┬──────────┘ └─┬─┘ └┬─┘ └────────┬─────────┘ └─────┬─────┘ └────┬────┘
        timestamp        PID  level     component         request_id    message
```

Extracted fields:

- `timestamp` - Log timestamp
- `severity` - Log level (`INFO`, `WARNING`, `ERROR`)
- `component` - Service component such as `nova.compute.manager`
- `request_id` - OpenStack request ID for tracing
- `message` - Log message content

#### Label enrichment

Adds Loki labels for efficient querying:

```yaml
processors:
  resource/loki-labels:
    attributes:
      - key: namespace
        from_attribute: k8s.namespace.name
      - key: pod
        from_attribute: k8s.pod.name
      - key: container
        from_attribute: k8s.container.name
      - key: service_name
        from_attribute: service.name
```

### Export to Loki

Processed logs are sent to Loki via OTLP/HTTP:

```yaml
exporters:
  otlphttp/loki:
    endpoint: "http://loki-gateway.monitoring.svc.cluster.local/otlp"

service:
  pipelines:
    logs/k8s:
      receivers:
        - filelog/k8s_containers
      processors:
        - memory_limiter
        - k8sattributes
        - batch
        - resource/loki-labels
      exporters:
        - otlphttp/loki
        - debug
```

## Loki log storage

### Overview

Loki is a horizontally scalable, highly available log aggregation system designed for cloud-native environments. Unlike traditional log systems, Loki only indexes labels instead of log content, which makes it much more cost-effective.

### Architecture

Loki is deployed with distributed components:

- **Gateway** - Receives logs from OpenTelemetry collectors
- **Distributor** - Routes logs to ingesters
- **Ingester** - Writes logs to storage and serves recent queries
- **Querier** - Serves log queries from storage
- **Compactor** - Compacts and manages stored logs

### Label-based indexing

Loki indexes logs based on labels, not content.

Traditional approach:

```text
Index every word in every log -> Large index -> High storage costs
```

Loki approach:

```text
Index only labels (namespace, pod, service) -> Small index -> Low storage costs
Query by labels, then search content -> Fast and efficient
```

### Storage tiers

#### Short-term storage (local)

- **Duration**: 24-72 hours
- **Storage**: Local PVCs on Kubernetes nodes
- **Purpose**: Fast queries for recent logs

#### Long-term storage (object storage)

- **Duration**: 30+ days, configurable
- **Storage**: S3, Swift, Ceph, or other object storage
- **Purpose**: Historical log retention and compliance

### Configuration

All configurations for Loki and OpenTelemetry are in:

- **Loki**: `genestack/base-helm-configs/loki`
- **OpenTelemetry**: `genestack/base-helm-configs/opentelemetry`

Review the default deployment settings and adjust them for your environment.

## Log storage operations

### How logs flow through the system

1. **Log generation in Kubernetes**

   Applications running in Kubernetes pods generate logs as part of their normal operation, recording events, errors, and other relevant information.

2. **OpenTelemetry collection**

   OpenTelemetry, deployed as a **DaemonSet**, runs on every node:

   - Collects logs from `/var/log/pods` in real time
   - Parses CRI format and extracts metadata
   - Handles multi-line logs such as stack traces and exceptions
   - Enriches logs with Kubernetes labels and attributes

3. **Processing and batching**

   OpenTelemetry processors:

   - Filter unwanted logs
   - Batch logs for efficient transmission
   - Add resource attributes for Loki labels
   - Rate limit to prevent overwhelming Loki

4. **Sending logs to Loki**

   Processed logs are sent to Loki via OTLP/HTTP:

   - Labels are indexed (`namespace`, `pod`, `service`)
   - Log content is stored but not indexed
   - Timestamps are preserved

5. **Loki indexing and storage**

   Loki receives and processes logs:

   - **Distributor** validates and routes logs
   - **Ingester** writes to local storage and memory
   - **Chunks** are created as compressed log blocks
   - Recent logs are kept in memory for fast queries

6. **Long-term storage**

   Loki chunks logs into large objects:

   - Chunks are compressed with gzip or snappy
   - Sent to object storage such as S3, Swift, or Ceph
   - Local storage is freed
   - Index remains small because only labels are indexed

7. **Object storage**

   OpenStack Swift, S3, or Ceph provides:

   - Durable storage for archived logs
   - Cost-effective long-term retention
   - Scalable capacity

### Key benefits of this architecture

- Efficient log collection with OpenTelemetry's lightweight design
- Cost-effective storage because Loki only indexes labels
- Scalable log aggregation with Loki's distributed architecture
- Flexible retention policies across local and object storage
- Powerful querying with LogQL and Grafana Explore
- Secure and reliable long-term storage using object storage

## Accessing logs through Grafana

The logs that Loki stores can be searched and analyzed through Grafana's Explore interface.

### Accessing Grafana

```bash
kubectl -n monitoring port-forward svc/grafana 3000:80

# Open browser to http://localhost:3000
# Username: admin
# Password: (from secret)
```

### Using Grafana Explore

From the left-side menu, select **Explore** to enter LogQL queries.

#### Step 1: Select the Loki datasource

Choose **Loki** from the datasource dropdown at the top.

#### Step 2: Build your query

##### Basic label filtering

Start by selecting labels to filter logs:

```logql
{namespace="openstack"}
```

Available labels:

- `namespace` - Kubernetes namespace (`openstack`, `kube-system`, `monitoring`)
- `pod` - Pod name
- `container` - Container name
- `service_name` - OpenStack service (`nova`, `neutron`, `keystone`)
- `application` - Application name
- `severity` - Log level

##### Combining labels

Use multiple labels to narrow results:

```logql
{namespace="openstack", service_name="nova"}
```

##### Searching log content

Filter by content using `|=` (contains) or `!=` (does not contain):

```logql
{namespace="openstack", service_name="nova"} |= "ERROR"
```

##### Regular expression search

Use `|~` for regex matching:

```logql
{namespace="openstack"} |~ "ERROR|CRITICAL|FATAL"
```

### Example queries

#### Find errors in the Nova service

```logql
{namespace="openstack", service_name="nova"} |= "ERROR"
```

#### Search for a specific project ID

```logql
{namespace="openstack", service_name="nova"} |= "project_id: abc-123-def"
```

#### Find logs for a specific server UUID

```logql
{namespace="openstack"} |= "server_uuid: 550e8400-e29b-41d4-a716-446655440000"
```

![grafana search](/assets/images/grafana-search.png)

#### Filter by request ID across services

```logql
{namespace="openstack"} |= "req-abc-123-def"
```

This shows all logs related to a single OpenStack request across all services.

#### Show only critical errors

```logql
{namespace="openstack", severity="ERROR"} |~ "CRITICAL|Exception"
```

#### Logs from a specific pod

```logql
{namespace="openstack", pod="nova-api-12345"}
```

#### Rate of errors over time

```logql
rate({namespace="openstack"} |= "ERROR" [5m])
```

This shows the rate of errors per second over five-minute windows.

#### Count logs by service

```logql
sum by (service_name) (count_over_time({namespace="openstack"}[1h]))
```

This shows log volume per OpenStack service in the last hour.

### Label matching operators

| Operator | Description | Example |
| --- | --- | --- |
| `=` | Exactly equal | `{namespace="openstack"}` |
| `!=` | Not equal | `{namespace!="kube-system"}` |
| `=~` | Regex matches | `{service_name=~"nova\\|neutron"}` |
| `!~` | Regex does not match | `{pod!~".*test.*"}` |

### Content matching operators

| Operator | Description | Example |
| --- | --- | --- |
| `|=` | Line contains | `|= "ERROR"` |
| `!=` | Line does not contain | `!= "DEBUG"` |
| `|~` | Line matches regex | `|~ "ERROR\\|CRITICAL"` |
| `!~` | Line does not match regex | `!~ "^INFO"` |

### Advanced query features

#### Parsing JSON logs

```logql
{namespace="openstack"} | json | severity="ERROR"
```

#### Extracting fields

```logql
{namespace="openstack"} | logfmt | severity="ERROR" | line_format "{{.timestamp}} {{.message}}"
```

#### Log context

View logs before and after a specific entry:

1. Click on a log line in Grafana.
2. Click **Show Context**.
3. Review the surrounding log entries.

#### Live tail

Stream logs in real time:

1. Click the **Live** button in Grafana Explore.
2. Logs appear as they are ingested.
3. Use this when debugging active issues.

## Common use cases

### Debugging application errors

Scenario: Nova API is returning 500 errors.

```logql
{namespace="openstack", service_name="nova"} |= "500" |= "ERROR"
```

Next steps:

1. Find the request ID in the log.
2. Search for that request ID across all services:

   ```logql
   {namespace="openstack"} |= "req-abc-123"
   ```

3. See the full request flow from API to database to compute.

### Monitoring failed operations

Scenario: Track failed volume attachments.

```logql
{namespace="openstack", service_name="cinder"} |= "attach" |= "failed"
```

Create alert:

```yaml
- name: volume-attach-failures
  expr: |
    rate({namespace="openstack", service_name="cinder"} |= "attach" |= "failed" [5m]) > 0.1
  annotations:
    summary: "High rate of volume attach failures"
```

### Security auditing

Scenario: Track all authentication failures.

```logql
{namespace="openstack", service_name="keystone"} |= "authentication" |= "failed"
```

### Performance investigation

Scenario: Find slow database queries.

```logql
{namespace="openstack"} |~ "query took [0-9]+\\.[0-9]+ seconds" | line_format "{{.message}}"
```

### Compliance and retention

Scenario: Export logs for compliance.

```bash
logcli --since=30d --quiet \
  '{namespace="openstack", service_name="keystone"}' \
  --output=jsonl \
  > keystone-audit-logs.jsonl
```

## Using logcli

### Installation

```bash
wget https://github.com/grafana/loki/releases/download/v2.9.0/logcli-linux-amd64.zip
unzip logcli-linux-amd64.zip
chmod +x logcli-linux-amd64
sudo mv logcli-linux-amd64 /usr/local/bin/logcli
```

### Configuration

```bash
export LOKI_ADDR=http://loki-gateway.monitoring.svc.cluster.local

# Or port-forward and use localhost
kubectl -n monitoring port-forward svc/loki-gateway 3100:80 &
export LOKI_ADDR=http://localhost:3100
```

### Example commands

#### Query logs

```bash
logcli query '{namespace="openstack", service_name="nova"}'
```

#### Search with time range

```bash
logcli query --since=1h '{namespace="openstack"} |= "ERROR"'
```

#### Tail logs

```bash
logcli query --tail '{namespace="openstack", service_name="nova"}'
```

#### Export logs

```bash
logcli query --since=24h --quiet \
  '{namespace="openstack"}' \
  --output=jsonl \
  > openstack-logs.jsonl
```

#### Search for a project ID

```bash
logcli query --since=15m \
  '{namespace="openstack", service_name=~"nova|placement"} |~ `project-id-abc-123`' \
  --output=raw
```

### logcli output formats

| Format | Description | Use case |
| --- | --- | --- |
| `default` | Human-readable with colors | Interactive terminal use |
| `raw` | Just the log messages | Piping to other tools |
| `jsonl` | JSON lines format | Structured log export |
| `labels` | Show labels only | Understanding log structure |

## Log retention and storage

### Retention policies

```yaml
limits_config:
  retention_period: 744h # 31 days

table_manager:
  retention_deletes_enabled: true
  retention_period: 744h
```

### Storage backends

#### S3

```yaml
storage_config:
  aws:
    s3: s3://region/bucket-name
    s3forcepathstyle: true
```

#### OpenStack Swift

```yaml
storage_config:
  swift:
    auth_url: https://keystone.example.com/v3
    username: loki
    project_name: monitoring
    region_name: RegionOne
    container_name: loki-logs
```

#### Ceph

```yaml
storage_config:
  aws:
    s3: s3://ceph-endpoint/loki-bucket
    s3forcepathstyle: true
```

### Compaction

Loki automatically compacts logs:

1. Chunks are created as ten-minute blocks.
2. Compaction merges small chunks.
3. Compacted chunks are uploaded to object storage.
4. Local storage is cleaned up.

## Troubleshooting

### No logs appearing

Check OpenTelemetry collectors:

```bash
kubectl -n monitoring logs daemonset/opentelemetry-kube-stack-daemon-collector | grep loki
```

Verify the logs collection preset:

```bash
kubectl get opentelemetrycollector -n monitoring opentelemetry-kube-stack-daemon -o yaml | grep -A 5 logsCollection
```

Expected:

```yaml
logsCollection:
  enabled: true
```

### Slow queries

Optimize by adding more specific labels.

Slow:

```logql
{namespace="openstack"} |= "error"
```

Faster:

```logql
{namespace="openstack", service_name="nova", severity="ERROR"}
```

### High storage usage

Check log volume:

```bash
logcli stats --since=24h '{namespace="openstack"}'
```

Reduce retention or filter noisy logs:

```yaml
processors:
  filter/drop-debug:
    logs:
      exclude:
        match_type: strict
        severity_texts: ["DEBUG", "TRACE"]
```

## Additional resources

### Documentation

- [Grafana Loki Official Documentation](https://grafana.com/docs/loki/latest/)
- [LogQL Query Language](https://grafana.com/docs/loki/latest/query/)
- [logcli Command Reference](https://grafana.com/docs/loki/latest/query/logcli/)
- [OpenTelemetry Filelog Receiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/filelogreceiver)
- [Genestack Observability Overview](/operations-guide/observability/observability-info/)
- [Getting Started with Monitoring](/deployment-guide/open-infrastructure/observability/getting-started/)

### Configuration files

- Loki Helm values: `genestack/base-helm-configs/loki`
- OpenTelemetry Helm values: `genestack/base-helm-configs/opentelemetry`
