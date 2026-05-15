---
title: "Blazar"
description: "Resource reservations in OpenStack."
weight: 120
---

[OpenStack Blazar](https://docs.openstack.org/blazar/latest/) is the resource reservation service in OpenStack. It enables tenants and operators to reserve resources (such as compute hosts) for a timeframe, supporting capacity planning and guaranteed availability use cases. This document outlines the deployment of OpenStack Blazar using Genestack.

## Create secrets

> [!note]
>
> Manual secret generation is only required if you haven't run the `create-secrets.sh` script located in `/opt/genestack/bin`.

**Example secret generation:**

```bash
kubectl --namespace openstack \
        create secret generic blazar-rabbitmq-password \
        --type Opaque \
        --from-literal=username="blazar" \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-64};echo;)"
kubectl --namespace openstack \
        create secret generic blazar-db-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
kubectl --namespace openstack \
        create secret generic blazar-admin \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
```

## Define policy configuration

> [!note]
>
> The default RabbitMQ policy sets quorum queues target group size to 3 for the `blazar` vhost. This can be changed in `base-kustomize/blazar/base/policies.yaml`.

Default RabbitMQ policy:

```yaml
apiVersion: rabbitmq.com/v1beta1
kind: Policy
metadata:
  name: blazar-quorum-three-replicas
  namespace: openstack
spec:
  name: blazar-quorum-three-replicas
  vhost: "blazar"
  pattern: ".*"
  applyTo: queues
  definition:
    target-group-size: 3
  priority: 0
  rabbitmqClusterReference:
    name: rabbitmq
```

## Add Blazar Filters

To add Blazar filters via an override file, create or update
`/etc/genestack/helm-configs/nova/nova-helm-overrides.yaml` with:

```yaml
conf:
  nova:
    filter_scheduler:
      available_filters: blazarnova.scheduler.filters.blazar_filter.BlazarFilter
      enabled_filters: BlazarFilter
```

## Run the package deployment

> [!genestack]
>
> Run the Blazar deployment script.

```bash {include="bin/install-blazar.sh"}
```

> [!TIP]
>
> You may need to provide custom values to configure your OpenStack services.
> For a simple single region or lab deployment you can supply an additional
> overrides flag using the example found at
> `base-helm-configs/aio-example-openstack-overrides.yaml`.

## Validate functionality

```bash
kubectl --namespace openstack exec -ti openstack-admin-client -- blazar host-list
```
