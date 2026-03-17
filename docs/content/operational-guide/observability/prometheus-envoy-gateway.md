---
title: "Envoy Gateway Monitoring"
weight: 600
---
Envoy Gateway exposes metrics that can be used to monitor the behavior and health of the Envoy Gateway.

Following the deployment of the [Envoy Gateway](/deployment-guide/infrastructure-envoy-gateway-api/) the metrics will be served and the service monitor will be created.

If you need to deploy the service monitor independently you may apply the file directly with the following directions.

## Installation

``` shell
kubectl apply -f /etc/genestack/kustomize/envoyproxy-gateway/base/envoy-service-monitor.yaml
```
