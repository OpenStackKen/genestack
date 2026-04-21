---
title: "PostgreSQL"
weight: 160
---
[PostgreSQL](https://www.postgresql.org/) is used by [Gnocchi](/deployment-guide/open-infrastructure/openstack/metering/gnocchi/) to index the data
collected and sent by [Ceilometer](/deployment-guide/open-infrastructure/openstack/metering/ceilometer/).

## Install the Postgres Operator

We are using the [Zalando postgres-operator](https://github.
com/zalando/postgres-operator/) which offers easy to run and
highly-available PostgreSQL clusters on Kubernetes.

Run the postgres-operator deployment Script `/opt/genestack/bin/install-postgres-operator.sh`

```bash {include="bin/install-postgres-operator.sh"}
```
```

```

## Create the PostgreSQL Cluster


### With kubectl _(Recommended)_


> [!NOTE]
>
> **Customize as needed**
>
>
> Be sure to modify the cluster parameters to suit your needs. The below
> values should work fine for a small lab or staging envionrment, however
> more disk space and other changes may be required in production.

```shell
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


Two overlays exist - `base` which includes 3 replicas, and an `aio` overlay
which has a single replica and less default resource utilization.

```shell
kubectl kustomize /etc/genestack/kustomize/postgres-cluster/overlay | kubectl apply -f -
```
