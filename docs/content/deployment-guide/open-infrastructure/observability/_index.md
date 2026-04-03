---
title: "Observability"
weight: 50
type: docs
simple_list: true
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
---
config:
  theme: base
  themeVariables:
    fontSize: 15px
    fontFamily: Inter, Helvetica, Arial
    primaryColor: '#1e90ff'
    primaryBorderColor: '#1e90ff'
    primaryTextColor: '#ffffff'
    lineColor: '#cccccc'
    secondaryColor: '#fafafa'
    tertiaryColor: '#f5f5f5'
    edgeLabelBackground: '#f5f5f5'
    nodeBorder: rgba(0,0,0,0.4)
    clusterBkg: transparent
    clusterBorder: rgba(0,0,0,0.4)
  flowchart:
    curve: basis
    nodeSpacing: 25
    rankSpacing: 40
  layout: dagre
---
flowchart TB
 subgraph PROMOPS["Prometheus&nbsp;Operations"]
    direction TB
        MC@{ label: "📦&nbsp;<b>Metric&nbsp;Collectors</b><br><span style=\"font-size:11px\">Node Exporter · Kube State · cAdvisor · RabbitMQ · MySQL · OpenStack · Postgres · Memcached</span>" }
        PROM(("🔥 Prometheus"))
        AM(("🔔 AlertManager"))
  end
 subgraph FLEX["Cluster"]
    direction TB
        PROMOPS
        GRAF@{ label: "🌀&nbsp;<b>Grafana</b><br><span style=\"font-size:11px\">Visualization&nbsp;dashboard</span>" }
        n1@{ label: "🌀<b>FluentD</b><br><span style=\"font-size:11px\">Log Shipping</span>" }
        n2@{ label: "<span style=\"padding-left:\">🌀<b>Liki</b><br><span style=\"font-size:11px\">Log Aggregation</span></span>" }
  end
 subgraph RACKSPACE["Datacenter"]
    direction TB
        FLEX
        ENC@{ label: "🗄️&nbsp;<b>Webhook&nbsp;Receiver</b><br><span style=\"font-size:11px\">(creates tickets)</span>" }
        n3@{ label: "🗄️<b>Swift</b><br><span style=\"font-size:11px\">(object storage)</span>" }
  end
 subgraph INTERNET[" "]
    direction LR
        PD["🌩️&nbsp;PagerDuty / Email / Slack"]
        RACKSPACE
  end
    MC -. Scrapes .-> PROM
    PROM -. Targets .-> MC
    PROM --> AM
    GRAF -- Queries --> PROM
    AM -- Alerts --> PD & ENC
    n1 --> n2
    n2 --> n3
    MC@{ shape: rect}
    GRAF@{ shape: rect}
    n1@{ shape: rect}
    n2@{ shape: rect}
    ENC@{ shape: rect}
    n3@{ shape: rect}
     MC:::collectorNode
     PROM:::promNode
     AM:::alertNode
     GRAF:::grafNode
     n1:::grafNode
     n2:::grafNode
     ENC:::miscNode
     n3:::miscNode
     PD:::miscNode
    classDef promNode      fill:#fff3e6,color:#000,stroke:#ff6600,stroke-width:1px
    classDef alertNode     fill:#ffe6e6,color:#800000,stroke:#ff4d4d,stroke-width:1px
    classDef collectorNode fill:#f2f8f2,color:#003300,stroke:#00b300,stroke-width:1px
    classDef miscNode      fill:#f2f2f2,color:#333,stroke:#999,stroke-width:1px
    classDef grafNode fill:#e6f0ff, color:#003366, stroke:#1e90ff, stroke-width:1px
    style PROMOPS   stroke-width:3px,stroke:#ff6600,rx:6px,ry:6px
    style n2 fill:#BBDEFB,color:#000000
    style FLEX      stroke-width:3px,stroke:#00b300,rx:6px,ry:6px
    style RACKSPACE stroke-width:3px,stroke:#ff4d4d,rx:6px,ry:6px
    style INTERNET  stroke-width:4px,stroke:#1e90ff,rx:6px,ry:6px
    linkStyle 0 color:#800080,font-weight:bold,fill:none
    linkStyle 1 color:#800080,font-weight:bold,fill:none
    linkStyle 2 color:#800080,font-weight:bold,fill:none
    linkStyle 3 color:#800080,font-weight:bold,fill:none
    linkStyle 4 color:#800080,font-weight:bold,fill:none
    linkStyle 5 color:#800080,font-weight:bold,fill:none
```

## Prerequisites

Before proceeding, ensure you have:

- A running Genestack deployment
- Helm 3.x installed
- Access to your Kubernetes cluster with appropriate permissions

This guide walks you through setting up a complete monitoring stack for your Genestack deployment. The monitoring system consists of three main layers: metrics collection, visualization, and alerting.

## Components
