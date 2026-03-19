---
title: "Setting up Loki"
weight: 150
---
Loki is a horizontally-scalable, highly-available, multi-tenant log aggregation system inspired by Prometheus. It is designed to be very cost-effective and easy to operate. It does not index the contents of the logs, but rather a set of labels for each log stream.

## Run the package deployment

> [!IMPORTANT]
> **Run the Loki deployment Script `/opt/genestack/bin/install-loki.sh`**
>
>
> ``` shell
> #!/bin/bash
> # Description: Fetches the version for SERVICE_NAME_DEFAULT from the specified
> # YAML file and executes a helm upgrade/install command with dynamic values files.
> 
> # Disable SC2124 (unused array), SC2145 (array expansion issue), SC2294 (eval)
> # shellcheck disable=SC2124,SC2145,SC2294
> 
> # Service
> SERVICE_NAME_DEFAULT="loki"
> SERVICE_NAMESPACE="grafana"
> 
> # Helm
> HELM_REPO_NAME_DEFAULT="grafana"
> HELM_REPO_URL_DEFAULT="https://grafana.github.io/helm-charts"
> 
> # Base directories provided by the environment
> GENESTACK_BASE_DIR="${GENESTACK_BASE_DIR:-/opt/genestack}"
> GENESTACK_OVERRIDES_DIR="${GENESTACK_OVERRIDES_DIR:-/etc/genestack}"
> 
> # Define service-specific override directories based on the framework
> SERVICE_BASE_OVERRIDES="${GENESTACK_BASE_DIR}/base-helm-configs/${SERVICE_NAME_DEFAULT}"
> SERVICE_CUSTOM_OVERRIDES="${GENESTACK_OVERRIDES_DIR}/helm-configs/${SERVICE_NAME_DEFAULT}"
> 
> # Define the Global Overrides directory used in the original script
> GLOBAL_OVERRIDES_DIR="${GENESTACK_OVERRIDES_DIR}/helm-configs/global_overrides"
> 
> # Read the desired chart version from VERSION_FILE
> VERSION_FILE="${GENESTACK_OVERRIDES_DIR}/helm-chart-versions.yaml"
> 
> if [ ! -f "$VERSION_FILE" ]; then
>     echo "Error: helm-chart-versions.yaml not found at $VERSION_FILE" >&2
>     exit 1
> fi
> 
> # Extract version dynamically using the SERVICE_NAME_DEFAULT variable
> SERVICE_VERSION=$(grep "^[[:space:]]*${SERVICE_NAME_DEFAULT}:" "$VERSION_FILE" | sed "s/.*${SERVICE_NAME_DEFAULT}: *//")
> 
> if [ -z "$SERVICE_VERSION" ]; then
>     echo "Error: Could not extract version for '$SERVICE_NAME_DEFAULT' from $VERSION_FILE" >&2
>     exit 1
> fi
> 
> echo "Found version for $SERVICE_NAME_DEFAULT: $SERVICE_VERSION"
> 
> # Load chart metadata from custom override YAML if defined
> for yaml_file in "${SERVICE_CUSTOM_OVERRIDES}"/*.yaml; do
>     if [ -f "$yaml_file" ]; then
>         HELM_REPO_URL=$(yq eval '.chart.repo_url // ""' "$yaml_file")
>         HELM_REPO_NAME=$(yq eval '.chart.repo_name // ""' "$yaml_file")
>         SERVICE_NAME=$(yq eval '.chart.service_name // ""' "$yaml_file")
>         break  # use the first match and stop
>     fi
> done
> 
> # Fallback to defaults if variables not set
> : "${HELM_REPO_URL:=$HELM_REPO_URL_DEFAULT}"
> : "${HELM_REPO_NAME:=$HELM_REPO_NAME_DEFAULT}"
> : "${SERVICE_NAME:=$SERVICE_NAME_DEFAULT}"
> 
> 
> # Determine Helm chart path
> if [[ "$HELM_REPO_URL" == oci://* ]]; then
>     # OCI registry path
>     HELM_CHART_PATH="$HELM_REPO_URL/$HELM_REPO_NAME/$SERVICE_NAME"
> else
>     # --- Helm Repository and Execution ---
>     helm repo add "$HELM_REPO_NAME" "$HELM_REPO_URL"
>     helm repo update
>     HELM_CHART_PATH="$HELM_REPO_NAME/$SERVICE_NAME"
> fi
> 
> # Debug output
> echo "[DEBUG] HELM_REPO_URL=$HELM_REPO_URL"
> echo "[DEBUG] HELM_REPO_NAME=$HELM_REPO_NAME"
> echo "[DEBUG] SERVICE_NAME=$SERVICE_NAME"
> echo "[DEBUG] HELM_CHART_PATH=$HELM_CHART_PATH"
> 
> # Prepare an array to collect -f arguments
> overrides_args=()
> 
> # Include all YAML files from the BASE configuration directory
> # NOTE: Files in this directory are included first.
> if [[ -d "$SERVICE_BASE_OVERRIDES" ]]; then
>     echo "Including base overrides from directory: $SERVICE_BASE_OVERRIDES"
>     for file in "$SERVICE_BASE_OVERRIDES"/*.yaml; do
>         # Check that there is at least one match
>         if [[ -e "$file" ]]; then
>             echo " - $file"
>             overrides_args+=("-f" "$file")
>         fi
>     done
> else
>     echo "Warning: Base override directory not found: $SERVICE_BASE_OVERRIDES"
> fi
> 
> # Include all YAML files from the GLOBAL configuration directory
> # NOTE: Files here override base settings and are applied before service-specific ones.
> if [[ -d "$GLOBAL_OVERRIDES_DIR" ]]; then
>     echo "Including global overrides from directory: $GLOBAL_OVERRIDES_DIR"
>     for file in "$GLOBAL_OVERRIDES_DIR"/*.yaml; do
>         if [[ -e "$file" ]]; then
>             echo " - $file"
>             overrides_args+=("-f" "$file")
>         fi
>     done
> else
>     echo "Warning: Global override directory not found: $GLOBAL_OVERRIDES_DIR"
> fi
> 
> # Include all YAML files from the custom SERVICE configuration directory
> # NOTE: Files here have the highest precedence.
> if [[ -d "$SERVICE_CUSTOM_OVERRIDES" ]]; then
>     echo "Including overrides from service config directory:"
>     for file in "$SERVICE_CUSTOM_OVERRIDES"/*.yaml; do
>         if [[ -e "$file" ]]; then
>             echo " - $file"
>             overrides_args+=("-f" "$file")
>         fi
>     done
> else
>     echo "Warning: Service config directory not found: $SERVICE_CUSTOM_OVERRIDES"
> fi
> 
> echo
> 
> # Collect all --set arguments.
> set_args=()
> 
> 
> helm_command=(
>     helm upgrade --install "$SERVICE_NAME_DEFAULT" "$HELM_CHART_PATH"
>     --version "${SERVICE_VERSION}"
>     --namespace="$SERVICE_NAMESPACE"
>     --timeout 120m
>     --create-namespace
> 
>     "${overrides_args[@]}"
>     "${set_args[@]}"
> 
>     # Post-renderer configuration
>     --post-renderer "$GENESTACK_OVERRIDES_DIR/kustomize/kustomize.sh"
>     --post-renderer-args "$SERVICE_NAME_DEFAULT/overlay"
> 
>     "$@"
> )
> 
> echo "Executing Helm command (arguments are quoted safely):"
> printf '%q ' "${helm_command[@]}"
> echo
> 
> # Execute the command directly from the array
> "${helm_command[@]}"
> ```
>

> [!TIP]
>
>
>

### Swift _(Recommended)_


> [!NOTE]
>
>
> If you plan on using **Swift** as a backend for log storage see the `loki-helm-swift-overrides-example.yaml` file in the `helm-configs/loki` directory.
>
> ``` yaml
> ---
> global:
>   dnsService: coredns
> minio:
>   enabled: false
> loki:
>   persistence:
>     enabled: true
>     size: 100Gi
>   auth_enabled: false
>   configStorageType: Secret
>   ingester:
>     autoforget_unhealthy: true
>   storage:
>     bucketNames:
>       chunks: LOKI_CHUNKS_BUCKET_NAME
>       ruler: LOKI_RULER_BUCKET_NAME
>       admin: LOKI_ADMIN_BUCKET_NAME
>     type: swift
>     swift:
>       auth_url: YOUR_SWIFT_AUTH_URL
>       password: YOUR_SWIFT_PASSWORD
>       username: YOUR_SWIFT_USERNAME
>       container_name: YOUR_SWIFT_CONTAINER_NAME
>       region_name: YOUR_SWIFT_REGION
>   schemaConfig:
>     configs:
>       - from: 2020-01-01
>         store: tsdb
>         object_store: swift
>         schema: v13
>         index:
>           prefix: index_
>           period: 24h
>   limits_config:
>     ingestion_rate_mb: 10
>     ingestion_burst_size_mb: 40
>     per_stream_rate_limit: 10MB
>     per_stream_rate_limit_burst: 40MB
> 
>   write:
>     replicas: 5
>     podDisruptionBudget:
>       enabled: true
>       maxUnavailable: 40%
>     nodeSelector:
>       openstack-control-plane: enabled
>     serviceMonitor:
>       enabled: true
> 
>   read:
>     podDisruptionBudget:
>       enabled: true
>       maxUnavailable: 40%
>     nodeSelector:
>       openstack-control-plane: enabled
>     serviceMonitor:
>       enabled: true
> 
>   canary:
>     enabled: true
>     podDisruptionBudget:
>       enabled: true
>       maxUnavailable: 50%
>     serviceMonitor:
>       enabled: true
> 
>   backend:
>     serviceMonitor:
>       enabled: true
> 
> gateway:
>   service:
>     type: NodePort
>     nodePort: 31776
>   podDisruptionBudget:
>     enabled: true
>     maxUnavailable: 1
>   nodeSelector:
>     openstack-control-plane: enabled
>   serviceMonitor:
>     enabled: true
> 
> lokiCanary:
>   kind: Deployment
>   replicas: 1
>   nodeSelector:
>     openstack-control-plane: enabled
> ```
>
>
>

### S3


> [!NOTE]
>
>
> If you plan on using **S3** as a backend for log storage see the `loki-helm-s3-overrides-example.yaml` file in the `helm-configs/loki` directory.
>
> ``` yaml
> ---
> global:
>   dnsService: coredns
> minio:
>   enabled: false
> loki:
>   persistence:
>     enabled: true
>     size: 100Gi
>   auth_enabled: false
>   configStorageType: Secret
>   ingester:
>     autoforget_unhealthy: true
>   storage:
>     bucketNames:
>       chunks: loki-chunks-bucket-name
>       ruler: loki-ruler-bucket-name
>       admin: loki-admin-bucket-name
>     type: s3
>     s3:
>       endpoint: YOUR_S3_ENDPOINT_URL
>       region: YOUR_S3_REGION
>       access_key_id: YOUR_S3_ACCESS_KEY_ID
>       secret_access_key: YOUR_S3_SECRET_ACCESS_KEY
>       s3forcepathstyle: true
>       insecure: false
>   schemaConfig:
>     configs:
>       - from: 2020-01-01
>         store: tsdb
>         object_store: s3
>         schema: v13
>         index:
>           prefix: index_
>           period: 24h
>   limits_config:
>     ingestion_rate_mb: 10
>     ingestion_burst_size_mb: 40
>     per_stream_rate_limit: 10MB
>     per_stream_rate_limit_burst: 40MB
> 
>   write:
>     replicas: 5
>     podDisruptionBudget:
>       enabled: true
>       maxUnavailable: 40%
>     nodeSelector:
>       openstack-control-plane: enabled
>     serviceMonitor:
>       enabled: true
> 
>   read:
>     podDisruptionBudget:
>       enabled: true
>       maxUnavailable: 40%
>     nodeSelector:
>       openstack-control-plane: enabled
>     serviceMonitor:
>       enabled: true
> 
>   canary:
>     enabled: true
>     podDisruptionBudget:
>       enabled: true
>       maxUnavailable: 50%
>     serviceMonitor:
>       enabled: true
> 
>   backend:
>     serviceMonitor:
>       enabled: true
> 
> gateway:
>   service:
>     type: NodePort
>     nodePort: 31776
>   podDisruptionBudget:
>     enabled: true
>     maxUnavailable: 1
>   nodeSelector:
>     openstack-control-plane: enabled
>   serviceMonitor:
>     enabled: true
> 
> lokiCanary:
>   kind: Deployment
>   replicas: 1
>   nodeSelector:
>     openstack-control-plane: enabled
> ```
>
>
>

### MinIO


> [!NOTE]
>
>
> If you plan on using **Minio** as a backend for log storage see the `loki-helm-s3-overrides-example.yaml` file in the `helm-configs/loki` directory.
>
> ``` yaml
> ---
> global:
>   dnsService: coredns
> minio:
>   enabled: true
> loki:
>   persistence:
>     enabled: true
>     size: 100Gi
>   auth_enabled: false
>   configStorageType: Secret
>   ingester:
>     autoforget_unhealthy: true
>   storage:
>     bucketNames:
>       chunks: LOKI_CHUNKS_BUCKET_NAME
>       ruler: LOKI_RULER_BUCKET_NAME
>       admin: LOKI_ADMIN_BUCKET_NAME
>     # Storage type and connection details are handled implicitly by the chart
>     # when MinIO is enabled, connecting via S3 protocol to the internal MinIO service.
>   schemaConfig:
>     configs:
>       - from: 2020-01-01
>         store: tsdb
>         object_store: s3  # MinIO is S3-compatible
>         schema: v13
>         index:
>           prefix: index_
>           period: 24h
>   limits_config:
>     ingestion_rate_mb: 10
>     ingestion_burst_size_mb: 40
>     per_stream_rate_limit: 10MB
>     per_stream_rate_limit_burst: 40MB
> 
>   write:
>     replicas: 5
>     podDisruptionBudget:
>       enabled: true
>       maxUnavailable: 40%
>     nodeSelector:
>       openstack-control-plane: enabled
>     serviceMonitor:
>       enabled: true
> 
>   read:
>     podDisruptionBudget:
>       enabled: true
>       maxUnavailable: 40%
>     nodeSelector:
>       openstack-control-plane: enabled
>     serviceMonitor:
>       enabled: true
> 
>   canary:
>     enabled: true
>     podDisruptionBudget:
>       enabled: true
>       maxUnavailable: 50%
>     serviceMonitor:
>       enabled: true
> 
>   backend:
>     serviceMonitor:
>       enabled: true
> 
> gateway:
>   service:
>     type: NodePort
>     nodePort: 31776
>   podDisruptionBudget:
>     enabled: true
>     maxUnavailable: 1
>   nodeSelector:
>     openstack-control-plane: enabled
>   serviceMonitor:
>     enabled: true
> 
> lokiCanary:
>   kind: Deployment
>   replicas: 1
>   nodeSelector:
>     openstack-control-plane: enabled
> ```
>
