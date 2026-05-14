---
title: "Ceilometer"
description: "OpenStack telemetry service."
weight: 30
---

OpenStack Ceilometer is the telemetry service within the OpenStack ecosystem, responsible for collecting and delivering usage data across various OpenStack services. Ceilometer plays a critical role in monitoring and metering the performance and resource consumption of cloud infrastructure, providing essential data for billing, benchmarking, and operational insights. By aggregating metrics such as CPU usage, network bandwidth, and storage consumption, Ceilometer enables cloud operators to track resource usage, optimize performance, and ensure compliance with service-level agreements. In this document, we will discuss the deployment of OpenStack Ceilometer using Genestack. With Genestack, the deployment of Ceilometer is made more efficient, ensuring that comprehensive and reliable telemetry data is available to support the effective management and optimization of cloud resources.

## Prerequisites

Ceilometer in Genestack depends on Gnocchi for metric storage and indexing.
Before installing Ceilometer, ensure the following are already healthy:

- [Gnocchi](/deployment-guide/open-infrastructure/openstack/metering/gnocchi/) is installed and `gnocchi-api` has ready endpoints.
- [PostgreSQL](/deployment-guide/open-infrastructure/infrastructure/postgresql/) is installed for Gnocchi indexer storage.
- A Ceph backend is available for Gnocchi metric storage.
  - Internal Ceph: [Rook (Ceph) - In Cluster](/deployment-guide/open-infrastructure/storage/internal/ceph/)
  - External Ceph: see the Ceph options in [Deploy Gnocchi](/deployment-guide/open-infrastructure/openstack/metering/gnocchi/)

If Gnocchi is not healthy, Ceilometer pods will remain in their init dependency
wait state until `gnocchi-api`, `ceilometer-db-sync`, and `ceilometer-ks-user`
are all resolved.

## Create Secrets

> [!NOTE]
>
> Manual secret generation is only required if you haven't run the `create-secrets.sh` script located in `/opt/genestack/bin`.

Example secret generation:

```bash
kubectl --namespace openstack create secret generic ceilometer-keystone-admin-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
kubectl --namespace openstack create secret generic ceilometer-keystone-test-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
kubectl --namespace openstack create secret generic ceilometer-rabbitmq-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
```

## Run the package deployment

> [!EXAMPLE]
>
> Run the Ceilometer deployment script.

```bash {include="bin/install-ceilometer.sh"}
```

> [!TIP]
>
> You may need to provide custom values to configure your OpenStack services.
> For a simple single-region or lab deployment, you can supply an additional
> overrides flag using the example found at
> `base-helm-configs/aio-example-openstack-overrides.yaml`. For multi-region
> environments, review the
> [Multi-Region Support](/operations-guide/genestack/multi-region/) workflow.

## Validate the deployment

### Confirm install idempotency

Run the install script a second time and confirm it completes without error.

```bash
sudo /opt/genestack/bin/install-ceilometer.sh
```

### Confirm Ceilometer pods are running

```bash
kubectl get jobs,pods -n openstack | grep ceilometer
```

Expected steady state:
- `ceilometer-db-sync` is `Complete`
- `ceilometer-ks-user` is `Complete`
- `ceilometer-central` is `Running`
- `ceilometer-compute` pods are `Running`
- `ceilometer-notification` pods are `Running`

### Capture pod resource usage

```bash
kubectl top pods -n openstack | grep ceilometer
```

## Verify Ceilometer Workers

As there is no Ceilometer API, we will do a quick validation against the
Gnocchi API via a series of `openstack metric` commands to confirm that
Ceilometer workers are ingesting metric and event data then persisting them
to storage.

### Verify metric resource types exist

The Ceilomter db-sync job will create the various resource types in Gnocchi.
Without them, metrics can't be stored, so let's verify they exist. The
output should include named resource types and some attributes for resources
like `instance`, `instance_disk`, `network`, `volume`, etc.

```bash
kubectl exec -it openstack-admin-client -n openstack -- openstack metric resource-type list
```

### Verify metric resources

Confirm that resources are populating in Gnocchi

```bash
kubectl exec -it openstack-admin-client -n openstack -- openstack metric resource list
```

### Verify metrics

Confirm that metrics can be retrieved from Gnocchi

```bash
kubectl exec -it openstack-admin-client -n openstack -- openstack metric list
```
