---
title: "Horizon"
description: "The OG OpenStack Dashboard."
weight: 20
---

OpenStack Horizon is the web-based dashboard for the OpenStack ecosystem, providing users with a graphical interface to manage and interact with OpenStack services. Horizon simplifies the management of cloud resources by offering an intuitive and user-friendly platform where users can launch instances, manage storage, configure networks, and monitor the overall health of their cloud environment. It serves as the central point of interaction for administrators and users alike, providing visibility and control over the entire cloud infrastructure. In this document, we will detail the deployment of OpenStack Horizon using Genestack. By leveraging Genestack, the deployment of Horizon is made more efficient, ensuring that users have seamless access to a robust and responsive interface for managing their private and public cloud environments.

## Create secrets

> [!NOTE]
>
> Manual secret generation is only required if you haven't run the `create-secrets.sh` script located in `/opt/genestack/bin`.

Example secret generation:

```bash
kubectl --namespace openstack \
        create secret generic horizon-secret-key \
        --type Opaque \
        --from-literal=username="horizon" \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-64};echo;)"
kubectl --namespace openstack \
        create secret generic horizon-db-password \
        --type Opaque \
        --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
```

## Run the package deployment

> [!EXAMPLE]
>
> Run the Horizon deployment script.

```bash {include="bin/install-horizon.sh"}
```

> [!TIP]
>
> You may need to provide custom values to configure your OpenStack services.
> For a simple single-region or lab deployment, you can supply an additional
> overrides flag using the example found at
> `base-helm-configs/aio-example-openstack-overrides.yaml`. For multi-region
> environments, review the
> [Multi-Region Support](/operations-guide/genestack/multi-region/) workflow.
