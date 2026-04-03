---
title: "Prometheus"
weight: 10
---

We are taking advantage of the prometheus community kube-prometheus-stack as well as other various components for monitoring and alerting. For more information, take a look at [Prometheus Kube Stack](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack).

> [!TIP]
>
> You may need to provide custom values to configure prometheus. For a simple 
> single region or lab deployment you can supply an additional overrides flag
> using the example found at `base-helm-configs/aio-example-openstack-overrides.yaml`.
>
> In other cases such as a multi-region deployment you may want to view the
> [Multi-Region Support](/operational-guide/multi-region-support/) guide to for a workflow
> solution.

## Installing Prometheus

The kube-prometheus-stack is the foundation of the Genestack monitoring infrastructure. It deploys and manages the core monitoring components, which include:

- **Prometheus Operator** - Manages the Prometheus cluster deployment lifecycle
- **Prometheus Server** - Collects and stores metrics from configured targets
- **AlertManager** - Handles alerts sent by Prometheus and routes them to notification channels (email, PagerDuty, Slack, etc.)
- **Node Exporter** - Collects hardware and OS-level metrics from cluster nodes
- **Kube State Metrics** - Exposes Kubernetes cluster state metrics

See the [Prometheus installation guide](/deployment-guide/open-infrastructure/observability/prometheus/) for detailed setup instructions.

Run the Prometheus deployment:

``` shell
/opt/genestack/bin/install-kube-prometheus-stack.sh
```

> [!SUCCESS]
>
> If the installation is successful, you should see the related exporter pods
> in the prometheus namespace.
> ``` shell
> kubectl -n prometheus get pods -l "release=kube-prometheus-stack"
> ```
