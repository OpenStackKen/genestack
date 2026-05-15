---
title: "Memcached"
weight: 100
---
## Deploy the Memcached Cluster

> [!genestack]
>
> Run the memcached deployment script `/opt/genestack/bin/install-memcached.sh`. 

You can include parameters to deploy `aio` or `base-monitoring`. Running the script without parameters deploys the default `base` configuration.

```bash {include="bin/install-memcached.sh"}
```
> [!tip]
>
> Memcached has a base configuration which is HA and production ready. If you're deploying on a small cluster the `aio` configuration may better suit the needs of the environment.

### Deploy the Memcached Cluster With Monitoring Enabled

View the [Memcached Exporter](/deployment-guide/open-infrastructure/observability/exporters/memcached/) instructions to install a HA-ready memcached cluster with monitoring and metric collection enabled.

## Verify readiness with the following command

```bash
kubectl --namespace openstack get horizontalpodautoscaler.autoscaling memcached -w
```

> [!important]
>
> For more information on how to enable memcached monitoring with Prometheus, see the [Memcached Exporter](/deployment-guide/open-infrastructure/observability/exporters/memcached/) documentation.
