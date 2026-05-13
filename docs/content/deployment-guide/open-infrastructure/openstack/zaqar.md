---
title: "Zaqar"
description: "OpenStack Message Queues as a Service (MQaaS)."
weight: 160
---

> [!GENESTACK]
>
> **TECH PREVIEW**
>
>

## Deploy Zaqar

Zaqar is a multi-tenant cloud messaging and notification service for web and mobile developers. It features a REST API which developers can use to send messages between various components of their SaaS and mobile applications.

OpenStack components can use Zaqar to inform events to end users and communication with guest agent that run in the "over-cloud" layer. This document outlines the deployment of OpenStack Zaqar using Genestack.

> [!warning]
>
> The Zaqar Websocket API is not supported for now in Genestack. It maybe added in a future release.
>

## Create secrets

> [!NOTE]
>
> Manual secret generation is only required if you haven't run the `create-secrets.sh` script located in `/opt/genestack/bin`.

**Example secret generation:**

```bash
kubectl --namespace openstack \
     create secret generic zaqar-rabbitmq-password \
     --type Opaque \
     --from-literal=username="zaqar" \
     --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-64};echo;)"
kubectl --namespace openstack \
     create secret generic zaqar-db-password \
     --type Opaque \
     --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
kubectl --namespace openstack \
     create secret generic zaqar-admin \
     --type Opaque \
     --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
```

## Run the package deployment

> [!genestack]
>
> Run the Zaqar deployment script `/opt/genestack/bin/install-zaqar.sh`.

```bash {include="bin/install-zaqar.sh"}
```

> [!tip]
>
> You may need to provide custom values to configure your OpenStack services. For a simple single region or lab deployment you can supply an additional overrides flag using the example found at `base-helm-configs/aio-example-openstack-overrides.yaml`.

## Validate functionality

```bash
kubectl --namespace openstack exec -ti openstack-admin-client -- openstack messaging queue list
```
