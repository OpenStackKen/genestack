---
title: "Cinder"
weight: 60
type: docs
description: "OpenStack block storage deployment workflows, storage backends, and supported storage options."
cascade:
  - type: docs
---

OpenStack Cinder is a core component of the OpenStack cloud computing platform, responsible for providing scalable, persistent block storage to cloud instances. It allows users to manage volumes, snapshots, and backups, enabling efficient storage operations within both private and public cloud environments. This document details the deployment of OpenStack Cinder within Genestack.

> Genestack facilitates the deployment process by leveraging Kubernetes' orchestration capabilities, ensuring seamless integration and management of Cinder services spanning across storage types, platforms and environments.

## Create secrets

> [!note]
>
> Manual secret generation is only required if you haven't run the `create-secrets.sh` script located in `/opt/genestack/bin`.

**Example secret generation**
```bash
kubectl --namespace openstack \
    create secret generic cinder-rabbitmq-password \
    --type Opaque \
    --from-literal=username="cinder" \
    --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-64};echo;)"
kubectl --namespace openstack \
     create secret generic cinder-db-password \
     --type Opaque \
     --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
kubectl --namespace openstack \
     create secret generic cinder-admin \
     --type Opaque \
     --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
```

## Run the package deployment

> [!genestack]
>
> To deploy Cinder, run the Cinder deployment script `/opt/genestack/bin/install-cinder.sh`.

```bash {include="bin/install-cinder.sh"}
```

> [!TIP]
>
>
> You may need to provide custom values to configure your openstack services, for a simple single region or lab deployment you can supply an additional overrides flag using the example found at `base-helm-configs/aio-example-openstack-overrides.yaml`.
> In other cases such as a multi-region deployment you may want to view the [Multi-Region Support](/operations-guide/genestack/multi-region/) guide to for a workflow solution.
>

> [!GENESTACK]
>
> **External Ceph Storage Backend**
>
>
> If Cinder will be deployed with an external Ceph storage backend, review the
> [OpenStack Cinder Ceph Store](/operations-guide/openstack/cinder/cinder-ceph-store/) operator
> documentation for additional steps and setup.
>
