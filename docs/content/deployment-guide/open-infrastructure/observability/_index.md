---
title: "Observability"
weight: 50
type: docs
description: "Monitoring, alerting, metrics, exporters, and dashboards."
cascade:
  - type: docs
---

As software systems have grown more complex, so has the challenge of handling the enormous growth of data streams from logs and metrics. Observability is a practice that absorbs that data and extends monitoring to help teams identify the root causes of issues. 

Observability provides the capability to understand and react to the state of the cloud. In contrast to monitoring alone, observability helps predict outcomes based on metrics to proactively optimize your systems and applications and not just troubleshoot failures.

## Observability in Genestack

The Genestack monitoring and observability stack includes:

- [Prometheus](https://prometheus.io) – Time-series database and metrics collection engine
- [Grafana](https://grafana.com/oss) – Visualization and dashboards
- [AlertManager](https://prometheus.io/docs/alerting/latest/alertmanager/) – Alert routing and notification management
- [Metric Exporters](https://prometheus.io/docs/instrumenting/exporters/) – Service-specific metrics collection for OpenStack components

``` mermaid
flowchart TB
 subgraph PROMOPS["Prometheus&nbsp;Operations"]
    direction LR
        MC@{ label: "📦&nbsp;&nbsp;<b>Metric&nbsp;Collectors</b><br><span style=\"font-size:0.85em\">Node Exporter · Kube State · cAdvisor · RabbitMQ · MySQL · OpenStack · Postgres · Memcached</span>" }
        PROM(("🔥&nbsp;&nbsp;Prometheus"))
        AM(("🔔&nbsp;&nbsp;AlertManager"))
  end
 subgraph FLEX["Cluster"]
    direction LR
        PROMOPS
        GRAF@{ label: "🌀&nbsp;<b>Grafana</b><br><span style=\"font-size:0.85em\">Visualization&nbsp;dashboard</span>" }
        FLUENTD@{ label: "🌀&nbsp;<b>FluentD</b><br><span style=\"font-size:0.85em\">Log Shipping</span>" }
        LOKI@{ label: "<span style=\"padding-left:\">🌀&nbsp;<b>LOKI</b><br><span style=\"font-size:0.85em\">Log Aggregation</span></span>" }
  end
 subgraph RACKSPACE["Datacenter"]
    direction LR
        FLEX
        ENC@{ label: "🗄️&nbsp;<b>Webhook&nbsp;Receiver</b><br><span style=\"font-size:0.85em\">(creates tickets)</span>" }
        SWIFT@{ shape: cyl, label: "🗄️&nbsp;<b>Swift</b><br><span style=\"font-size:0.85em\">(object storage)</span>" }
  end

RACKSPACE
PD@{ shape: cloud, label: "🌩️&nbsp;&nbsp;PagerDuty/<br>Email/<br>Slack" }

    MC -. Scrapes .-> PROM
    PROM -. Targets .-> MC
    PROM --> AM
    GRAF -- Queries --> PROM
    AM -- Alerts --> PD & ENC
    FLUENTD --> LOKI
    LOKI --> SWIFT
    MC@{ shape: rect}
    GRAF@{ shape: rect}
    FLUENTD@{ shape: rect}
    LOKI@{ shape: rect}
    ENC@{ shape: rect}
    SWIFT@{ shape: rect}
     MC:::collectorNode
     PROM:::promNode
     AM:::alertNode
     GRAF:::grafNode
     FLUENTD:::grafNode
     LOKI:::grafNode
     ENC:::miscNode
     SWIFT:::miscNode
     PD:::miscNode
    classDef promNode       fill:#fff3e6,color:#000,stroke:#ff6600,stroke-width:1px
    classDef alertNode      fill:#ffe6e6,color:#800000,stroke:#ff4d4d,stroke-width:1px
    classDef collectorNode  fill:#f2f8f2,color:#003300,stroke:#00b300,stroke-width:1px
    classDef miscNode       fill:#f2f2f2,color:#333,stroke:#999,stroke-width:1px
    classDef grafNode       fill:#e6f0ff, color:#003366, stroke:#1e90ff, stroke-width:1px
    style LOKI      fill:#BBDEFB,color:#000000
    style PROMOPS   stroke-width:3px,rx:6px,ry:6px,padding:25px,line-height:2
    style FLEX      stroke-width:3px,rx:6px,ry:6px,padding:25px,line-height:2
    style RACKSPACE stroke-width:3px,rx:6px,ry:6px,padding:25px,line-height:2
    linkStyle 0 color:#800080,font-weight:bold,background-color:none;
    linkStyle 1 color:#800080,font-weight:bold,background-color:none;
    linkStyle 2 color:#800080,font-weight:bold,background-color:none;
    linkStyle 3 color:#800080,font-weight:bold,background-color:none;
    linkStyle 4 color:#800080,font-weight:bold,background-color:none;
    linkStyle 5 color:#800080,font-weight:bold,background-color:none;
```

## Prerequisites

Before proceeding, ensure you have:

- A running Genestack deployment
- Helm 3.x installed
- Access to your Kubernetes cluster with appropriate permissions

This guide walks you through setting up a complete monitoring stack for your Genestack deployment. The monitoring system consists of three main layers: metrics collection, visualization, and alerting.

## Components
