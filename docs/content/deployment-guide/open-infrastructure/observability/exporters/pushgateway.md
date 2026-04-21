---
title: "Pushgateway Exporter"
weight: 110
---

Prometheus can use a [pushgateway](https://prometheus.io/docs/practices/pushing/) to gather metrics from short-lived jobs. The pushgateway stays up to allow Promethus to gather the metrics. The short-lived job can then push metrics to the gateway and terminate.

> [!GENESTACK]
>
> Genestack uses pushgateway to collect metrics from the OVN backup `CronJob`.

## Installation

Install the PushGateway Exporter

`/opt/genestack/bin/install-prometheus-pushgateway.sh`

```bash {include="bin/install-prometheus-pushgateway.sh"}
```
```

```

> [!SUCCESS]
>
> If the installation is successful, you should see the prometheus-pushgateway pod running in the prometheus namespace.
