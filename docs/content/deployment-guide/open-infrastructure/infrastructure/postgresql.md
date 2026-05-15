---
title: "PostgreSQL"
weight: 160
---
[PostgreSQL](https://www.postgresql.org/) is used by [Gnocchi](/deployment-guide/open-infrastructure/openstack/metering/gnocchi/) to index the data collected and sent by [Ceilometer](/deployment-guide/open-infrastructure/openstack/metering/ceilometer/).

## Install the Postgres Operator

We are using the [Zalando postgres-operator](https://github.
com/zalando/postgres-operator/) which offers easy to run and
highly-available PostgreSQL clusters on Kubernetes.

> [!genestack]
>
> Run the postgres-operator deployment script.

```bash {include="bin/install-postgres-operator.sh"}
```

## Create the PostgreSQL Cluster

### With kubectl _(Recommended)_

> [!NOTE]
>
> Customize these cluster parameters to suit your environment. The example
> below is reasonable for a small lab or staging environment, but production
> deployments may require more storage and different PostgreSQL tuning.

```bash
kubectl apply -f - <<EOF
apiVersion: "acid.zalan.do/v1"
kind: postgresql
metadata:
  name: postgres-cluster
  namespace: openstack
spec:
  dockerImage: ghcr.io/zalando/spilo-16:3.2-p3
  teamId: "acid"
  numberOfInstances: 3
  postgresql:
    version: "16"
    parameters:
      shared_buffers: "2GB"
      max_connections: "1024"
      log_statement: "all"
  volume:
    size: 40Gi
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: node-role.kubernetes.io/worker
              operator: In
              values:
                - worker
EOF
```

### With kubectl kustomize Overlay

Two overlays exist - `base` which includes 3 replicas, and an `aio` overlay, which has a single replica and less default resource utilization.

```bash
kubectl kustomize /etc/genestack/kustomize/postgres-cluster/overlay | kubectl apply -f -
```
