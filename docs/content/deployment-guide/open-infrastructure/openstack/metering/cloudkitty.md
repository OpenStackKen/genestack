---
title: "CloudKitty"
description: "OpenStack Rating and Charge-Back Service"
weight: 40
---

[CloudKitty](https://docs.openstack.org/cloudkitty/latest/) is the rating and charge-back service for OpenStack  helps operators measure, rate, and bill tenants (projects) for the resources they consume in an OpenStack cloud. 

This document outlines the deployment of OpenStack Cloudkitty using Genestack.

## Create secrets

> [!NOTE]
>
> Manual secret generation is only required if you haven't run the
> `create-secrets.sh` script located in `/opt/genestack/bin`.

Example secret generation

``` shell
kubectl --namespace openstack \
        create secret generic cloudkitty-rabbitmq-password \
        --type Opaque \
        --from-literal=username="cloudkitty" \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-64};echo;)"
kubectl --namespace openstack \
        create secret generic cloudkitty-db-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
kubectl --namespace openstack \
        create secret generic cloudkitty-admin \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
```

## Run the package deployment

Run the Cloudkitty deployment Script `/opt/genestack/bin/install-cloudkitty.sh`

```bash {include="bin/install-cloudkitty.sh"}
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
kubectl --namespace openstack exec -ti openstack-admin-client -- openstack rating module list
```
