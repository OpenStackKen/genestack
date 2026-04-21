---
title: "Memcached"
weight: 100
---
## Deploy the Memcached Cluster

Run the memcached deployment Script `/opt/genestack/bin/install-memcached.sh` You can include parameters to deploy aio or base-monitoring. No parameters deploys base

```bash {include="bin/install-memcached.sh"}
```
> [!NOTE]
>
> Memcached has a base configuration which is HA and production ready. If you're deploying on a small cluster the `aio` configuration may better suit the needs of the environment.

### Alternative - Deploy the Memcached Cluster With Monitoring Enabled

View the [memcached exporter](/deployment-guide/open-infrastructure/observability/prometheus-memcached-exporter/) instructions to install a HA ready memcached cluster with monitoring and metric collection enabled.

## Verify readiness with the following command

``` shell
kubectl --namespace openstack get horizontalpodautoscaler.autoscaling memcached -w
```

> [!IMPORTANT]
>
> For more information on how to enable memcached monitoring with prometheus, see the [memcached exporter](/deployment-guide/open-infrastructure/observability/prometheus-monitoring-overview/) documentation.
