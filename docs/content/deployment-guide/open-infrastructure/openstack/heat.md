---
title: "Heat"
description: "OpenStack native orchestration service."
weight: 40
---

[OpenStack Heat](https://docs.openstack.org/heat/latest/) is the orchestration service within the OpenStack ecosystem, designed to automate the deployment of cloud applications by orchestrating infrastructure resources such as compute instances, storage volumes, and networking components. Heat allows users to define the infrastructure and application stack in a template format, which can then be deployed and managed as a single unit. This capability facilitates the automated, repeatable, and consistent deployment of complex cloud environments, reducing manual intervention and minimizing errors.

In this section, we will cover the deployment of OpenStack Heat using Genestack. With Genestack, the deployment of Heat is optimized, ensuring that cloud applications are efficiently orchestrated and managed, leading to improved scalability and reliability.

## Create secrets

> [!note]
>
> Manual secret generation is only required if you haven't run the `create-secrets.sh` script located in `/opt/genestack/bin`.

**Manual secret generation:**

```bash
kubectl --namespace openstack \
        create secret generic heat-rabbitmq-password \
        --type Opaque \
        --from-literal=username="heat" \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-64};echo;)"
kubectl --namespace openstack \
        create secret generic heat-db-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
kubectl --namespace openstack \
        create secret generic heat-admin \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
kubectl --namespace openstack \
        create secret generic heat-trustee \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
kubectl --namespace openstack \
        create secret generic heat-stack-user \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
```

## Run the package deployment

> [!genestack]
>
> Run the Heat deployment script `/etc/genestack/bin/install-heat.sh`.

```bash {include="bin/install-heat.sh"}
```

> [!tip]
>
> You may need to provide custom values to configure your OpenStack services. For a simple single-region or lab deployment, you can supply an additional overrides flag using the example found at `base-helm-configs/aio-example-openstack-overrides.yaml`. For multi-region environments, review the
> [Multi-Region Support](/operations-guide/genestack/multi-region/) workflow.

## Validate functionality

```bash
kubectl --namespace openstack exec -ti openstack-admin-client -- openstack --os-interface internal orchestration service list
```
