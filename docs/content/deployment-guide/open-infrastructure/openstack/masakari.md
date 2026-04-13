---
title: "Masakari"
description: "VM instance high-availability (HA) in OpenStack."
weight: 150
---

[Masakari](https://docs.openstack.org/masakari/latest/) is the High Availability (HA) service for instances (VMs) in OpenStack. Masakari provides instance HA by automatically recovering virtual machine workloads when the following failure modes occur:

- Compute host failures (node crashes, hardware failure)
- VM process failures (QEMU process crashes).
- Guest OS failures (detected through monitoring agents).

This section outlines the deployment of OpenStack Masakari using Genestack.

## Create secrets

> [!NOTE]
>
> Manual secret generation is only required if you haven't run the
> `create-secrets.sh` script located in `/opt/genestack/bin`.

Example secret generation

``` shell
kubectl --namespace openstack \
        create secret generic masakari-rabbitmq-password \
        --type Opaque \
        --from-literal=username="masakari" \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-64};echo;)"
kubectl --namespace openstack \
        create secret generic masakari-db-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
kubectl --namespace openstack \
        create secret generic masakari-admin \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
```

## Run the package deployment

Run the Masakari deployment Script `/opt/genestack/bin/install-masakari.sh`

```bash {include="bin/install-masakari.sh"}
```
```

```

> [!TIP]
>
> You may need to provide custom values to configure your OpenStack services.
> For a simple single region or lab deployment you can supply an additional
> overrides flag using the example found at
> `base-helm-configs/aio-example-openstack-overrides.yaml`.

## Validate functionality

``` shell
kubectl --namespace openstack exec -ti openstack-admin-client -- openstack segment list
```
