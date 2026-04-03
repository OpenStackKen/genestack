---
title: "Exporters"
weight: 30
---

Prometheus makes use of various metric [exporters](https://prometheus.io/docs/instrumenting/exporters/) used to collect monitoring data related to specific services:

- Node Exporter(Hardware metrics)
- Kube State Exporter(Kubernetes cluster metrics)
- Mysql Exporter(MariaDB/Galera metrics)
- RabbitMQ Exporter(RabbitMQ queue metrics)
- Postgres Exporter(Postgresql metrics)
- Memcached Exporter(Memcached metrics)
- Openstack Exporter(Metrics from various Openstack products)
- Pushgateway (metrics from short-lived jobs)
- SNMP exporter (for monitoring with SNMP)

With the core monitoring stack in place, deploy exporters to collect metrics from your OpenStack services and infrastructure components. Many exporters are included for easy deployment.

## Included Exporters
