---
title: "MariaDB Operator Upgrade Runbook"
---

Unified procedure for upgrading the MariaDB Operator Helm chart through the
required progressive upgrade path. Sequential upgrades are mandatory due to
CRD evolution and changes in replication and backup behaviour across versions.

> [!NOTE]
>
> Upgrade path:
>
> ```text
> 0.36.0 → 0.37.1 → 0.38.1 → 25.8.4 → 25.10.4 → 26.3.0
> ```

> [!WARNING]
>
> Never delete CRDs during the upgrade. Doing so will delete the MariaDB database pods. Uninstalling the operator Helm release alone does **not** cause database downtime.

## Prerequisites

### Check current installed versions

```bash
helm list -A | grep mariadb
helm status mariadb-operator -n mariadb-system
helm status mariadb-operator-crds -n mariadb-system
```

### Update Helm repo and list available chart versions

```bash
helm repo update mariadb-operator
helm search repo mariadb-operator/mariadb-operator --versions | head -20
```

## Pre-Upgrade Checks

> [!NOTE]
>
> Repeat these checks before **every** upgrade step.

### Retrieve the MariaDB root password

```bash
export MARIADB_ROOT_PASSWORD=$(kubectl get secret mariadb -n openstack \
  -o jsonpath='{.data.root-password}' | base64 -d)
```

### Create a full database backup

```bash
PRIMARY_POD=$(kubectl get mariadb mariadb-cluster -n openstack -o jsonpath="{.status.currentPrimary}")
echo "Primary pod: $PRIMARY_POD"
```

```bash
kubectl exec -i "$PRIMARY_POD" -n openstack -- mariadb-dump \
  -u root -p"$MARIADB_ROOT_PASSWORD" \
  --all-databases \
  --single-transaction \
  --routines \
  --triggers > mariadb-cluster-full-backup-$(date +%Y%m%d-%H%M).sql
```

```bash
ls -lh mariadb-cluster-full-backup-*.sql | tail -1
```

### Check database sizes

```bash
kubectl exec -it "$PRIMARY_POD" -n openstack -- mariadb -u root -p"$MARIADB_ROOT_PASSWORD" -e "
SELECT
  table_schema AS 'Database',
  ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size_MB'
FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')
GROUP BY table_schema
ORDER BY Size_MB DESC;"
```

### Verify cluster health

Determine your cluster topology and run the appropriate checks.

#### Galera cluster

```bash
kubectl exec -it "$PRIMARY_POD" -n openstack -- mariadb -u root -p"$MARIADB_ROOT_PASSWORD" -e "
SHOW STATUS LIKE 'wsrep_cluster_size';
SHOW STATUS LIKE 'wsrep_cluster_status';
SHOW STATUS LIKE 'wsrep_ready';"
```

Expected values:

| Variable | Expected |
| --- | --- |
| `wsrep_cluster_size` | `3` |
| `wsrep_cluster_status` | `Primary` |
| `wsrep_ready` | `ON` |

#### Primary/Replica (Replication)

Check the primary:

```bash
kubectl get mariadb mariadb-cluster -n openstack -o jsonpath="{.status.currentPrimary}"
```

Check replication status on each replica:

```bash
kubectl exec -it mariadb-cluster-1 -n openstack -- mariadb -u root -p"$MARIADB_ROOT_PASSWORD" -e "
SHOW REPLICA STATUS\G"
```

Expected values:

| Variable | Expected |
| --- | --- |
| `Slave_IO_Running` | `Yes` |
| `Slave_SQL_Running` | `Yes` |
| `Seconds_Behind_Master` | `0` |

> [!TIP]
>
> To identify your topology, check the MariaDB CR spec:
>
> ```bash
> kubectl get mariadb mariadb-cluster -n openstack -o jsonpath="{.spec.galera.enabled}"
> ```
>
> - Returns `true` → Galera cluster
> - Returns empty or `false` → Primary/Replica (replication)

### Verify cluster and pod status

```bash
kubectl get mariadb -n openstack
kubectl get pods -l app.kubernetes.io/name=mariadb -n openstack
kubectl get mariadb -n openstack -o yaml | grep -B1 autoFailover
kubectl get crd | grep mariadb
```

> [!NOTE]
>
> The `autoFailover` field is only present on versions `>= 25.10.4`.

### Verify current operator, webhook, and MariaDB image versions

#### Operator image

```bash
kubectl get pods -n mariadb-system -o wide

kubectl get pods \
  $(kubectl get pods \
  -l app.kubernetes.io/name=mariadb-operator \
  -n mariadb-system \
  -o jsonpath='{.items[0].metadata.name}') \
  -n mariadb-system \
  -o jsonpath="{..image}" | tr -s '[:space:]' '\n' | sort -u
```

#### Webhook image

```bash
kubectl get pods \
  $(kubectl get pods \
  -l app.kubernetes.io/name=mariadb-operator-webhook \
  -n mariadb-system \
  -o jsonpath='{.items[0].metadata.name}') \
  -n mariadb-system \
  -o jsonpath="{..image}" | tr -s '[:space:]' '\n' | sort -u
```

#### MariaDB image

```bash
kubectl get pods "$PRIMARY_POD" \
  -n openstack \
  -o jsonpath="{..image}" \
  | tr -s '[:space:]' '\n' | sort -u
```

## Upgrade Procedure

Repeat this procedure for each version in the upgrade path.

### Preflight: update the MariaDB image and enable `autoUpdateDataPlane`

Update the MariaDB image in `/opt/genestack/base-kustomize/mariadb-cluster/base/mariadb-replication.yaml` to match the version compatible with the operator chart version being deployed. With every release update you must update this image **before** upgrading the `mariadb-cluster`.

For replication clusters, treat this file as the canonical MariaDB baseline. In addition to the image tag, preserve the crash-safe replication settings (`binlog_format=ROW`, `innodb_flush_log_at_trx_commit=1`, `sync_binlog=1`) and the compatibility defaults (`character-set-server=utf8mb3`, `collation-server=utf8mb3_general_ci`) required for Alembic migrations against older OpenStack tables.

#### Finding the compatible MariaDB image

Check the `config.mariadbImage` value in the upstream chart `values.yaml` at the corresponding tag:

```text
https://github.com/mariadb-operator/mariadb-operator/blob/v<VERSION>/deploy/charts/mariadb-operator/values.yaml
```

For example, for chart version `25.8.4`:

```text
https://github.com/mariadb-operator/mariadb-operator/blob/v25.8.4/deploy/charts/mariadb-operator/values.yaml
```

If you inspect that file, you will see `mariadbImage: docker-registry1.mariadb.com/library/mariadb:11.8.2`.

Update the image in the base manifest. Example for a move to `25.8.4`:

```yaml {title="mariadb-replication.yaml"}
spec:
  image: docker-registry1.mariadb.com/library/mariadb:11.8.2
```

Then set `autoUpdateDataPlane: true` using one of the following methods.

#### Kustomize overlay (recommended)

Edit `/etc/genestack/kustomize/mariadb-cluster/overlay/kustomization.yaml`:

```yaml {title="kustomization.yaml"}
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../galera

patches:
  - target:
      kind: MariaDB
      name: mariadb-cluster
      namespace: openstack
    patch: |-
      - op: replace
        path: /spec/updateStrategy/autoUpdateDataPlane
        value: true
```

#### Base manifest

Edit `/etc/genestack/kustomize/mariadb-cluster/base/mariadb-replication.yaml`:

```yaml {title="mariadb-replication.yaml"}
spec:
  updateStrategy:
    autoUpdateDataPlane: true
```

> [!IMPORTANT]
>
> `autoUpdateDataPlane` uses a **ReplicasFirstPrimaryLast** strategy instead of **RollingUpdate**.
>
> - **Galera**: Updates replica nodes first, then the primary, which helps preserve quorum during the rollout.
> - **Primary/Replica**: Updates replicas first, then the primary, which reduces write downtime and data inconsistency risk.

Apply the changes:

```bash
kubectl --namespace openstack apply -k /etc/genestack/kustomize/mariadb-cluster/overlay
```

### Step 1: Scale down the operator and remove webhooks

```bash
kubectl scale deployment mariadb-operator -n mariadb-system --replicas=0
kubectl scale deployment mariadb-operator-webhook -n mariadb-system --replicas=0
kubectl delete validatingwebhookconfiguration mariadb-operator-webhook
kubectl delete mutatingwebhookconfiguration mariadb-operator-webhook 2>/dev/null || true
```

### Step 2: Update the chart version

Edit `/etc/genestack/helm-chart-versions.yaml`:

```yaml {title="helm-chart-versions.yaml"}
mariadb-operator: <TARGET_VERSION>
```

Confirm the version has been set:

```bash
grep mariadb-operator /etc/genestack/helm-chart-versions.yaml
```

### Step 3: Uninstall and reinstall the operator

```bash
helm uninstall mariadb-operator -n mariadb-system
/opt/genestack/bin/install-mariadb-operator.sh
```

### Step 4: Verify deployment

```bash
helm list -A | grep mariadb
kubectl get pods -n mariadb-system -o wide
kubectl get pods <new-operator-pod> -n mariadb-system \
  -o jsonpath="{..image}" | tr -s '[:space:]' '\n' | sort -u
```

### Step 5: Post-upgrade validation

```bash
kubectl get pods -n openstack | grep mariadb
kubectl get mariadb -n openstack
```

Run the cluster health checks from the pre-upgrade section again.

### Step 6: Disable `autoUpdateDataPlane`

Set `autoUpdateDataPlane: false` as described in the preflight section and re-apply:

```bash
kubectl --namespace openstack apply -k /etc/genestack/kustomize/mariadb-cluster/overlay
```

### Step 7: Run the migration for replication clusters

> [!WARNING]
>
> This step is only required for **Primary/Replica (replication)** clusters. If you are running a **Galera** cluster, skip it.

After the operator upgrade, you must run the replication migration script to reset and re-establish replication on each replica pod.

The script automatically identifies the primary pod, skips it, and processes only replicas. For each replica it:

- Runs `STOP SLAVE` and `RESET SLAVE ALL`
- Deletes the pod so it gets recreated
- Waits for the pod to become ready
- Verifies that replication is healthy again

Set the required environment variables:

```bash
export MARIADB_NAME=mariadb-cluster
export MARIADB_NAMESPACE=openstack
export MARIADB_ROOT_PASSWORD=$(kubectl get secret mariadb -n openstack \
  -o jsonpath='{.data.root-password}' | base64 -d)
```

Save the script to a file such as `/tmp/migrate-replication.sh`:

```bash {title="migrate-replication.sh"}
#!/bin/bash

set -eo pipefail

if [[ -z "$MARIADB_NAME" || -z "$MARIADB_NAMESPACE" || -z "$MARIADB_ROOT_PASSWORD" ]]; then
  echo "Error: MARIADB_NAME, MARIADB_NAMESPACE and MARIADB_ROOT_PASSWORD env vars must be set."
  exit 1
fi

function exec_sql {
  local pod=$1
  local sql=$2
  kubectl exec -n "$MARIADB_NAMESPACE" "$pod" -- mariadb -u root -p"$MARIADB_ROOT_PASSWORD" -e "$sql"
}

function wait_for_ready_replication {
  local pod=$1
  local timeout=300
  local interval=10
  local elapsed=0

  echo "Waiting for ready replication on $pod..."

  while [[ $elapsed -lt $timeout ]]; do
      local status
      status=$(exec_sql "$pod" "SHOW REPLICA STATUS\\G" | tee /tmp/replication_status_$pod_$MARIADB_NAMESPACE.txt)

      if grep -q "Slave_IO_Running: Yes" /tmp/replication_status_$pod_$MARIADB_NAMESPACE.txt && \
         grep -q "Slave_SQL_Running: Yes" /tmp/replication_status_$pod_$MARIADB_NAMESPACE.txt; then
        echo "Replication is ready on $pod."
        return 0
      fi

      echo "Replication not ready on $pod. Retrying in $interval seconds..."
      sleep $interval
      ((elapsed+=interval))
  done

  echo "Error: Replication did not become ready on $pod within 5 minutes."
  exit 1
}

echo "Migrating replication on $MARIADB_NAME instance..."

PODS=$(kubectl get pods -n "$MARIADB_NAMESPACE" \
  -l app.kubernetes.io/instance=$MARIADB_NAME \
  -o jsonpath="{.items[*].metadata.name}")
PRIMARY_POD=$(kubectl get mariadb "$MARIADB_NAME" -n "$MARIADB_NAMESPACE" \
  -o jsonpath="{.status.currentPrimary}")

for POD in $PODS; do
  if [[ "$POD" == "$PRIMARY_POD" ]]; then
      printf "\nSkipping primary pod: $POD\n"
      continue
  fi
  printf "\nProcessing replica pod: $POD\n"

  echo "Resetting replication on $POD..."
  exec_sql "$POD" "STOP SLAVE 'mariadb-operator';"
  exec_sql "$POD" "RESET SLAVE 'mariadb-operator' ALL;"

  echo "Deleting pod $POD..."
  kubectl delete pod "$POD" -n "$MARIADB_NAMESPACE"

  echo "Waiting for pod $POD to become ready..."
  kubectl wait --for=condition=Ready pod/"$POD" -n "$MARIADB_NAMESPACE" --timeout=5m
  echo "Pod $POD is ready."

  wait_for_ready_replication "$POD"
done

echo "Replication migration completed successfully on $MARIADB_NAME instance."
```

Make it executable and run it:

```bash
chmod +x /tmp/migrate-replication.sh
/tmp/migrate-replication.sh
```

> [!TIP]
>
> If stuck replication threads are observed, identify and kill them:
>
> ```bash
> kubectl exec -it mariadb-cluster-1 -n openstack -- mariadb \
>   -u root -p"$MARIADB_ROOT_PASSWORD" -e "SHOW PROCESSLIST;"
> kubectl exec -it mariadb-cluster-1 -n openstack -- mariadb \
>   -u root -p"$MARIADB_ROOT_PASSWORD" -e "KILL <thread_id>;"
> ```

## Recommended Upgrade Sequence

### 0.36.0 → 0.37.1

```bash
helm upgrade --install mariadb-operator-crds mariadb-operator/mariadb-operator-crds \
  --namespace mariadb-system \
  --version 0.37.1

helm upgrade --install mariadb-operator mariadb-operator/mariadb-operator \
  --namespace mariadb-system \
  --version 0.37.1
```

Follow the standard procedure above. No special handling beyond the standard checks is required.

### 0.37.1 → 0.38.1

```bash
helm upgrade --install mariadb-operator-crds mariadb-operator/mariadb-operator-crds \
  --namespace mariadb-system \
  --version 0.38.1

helm upgrade --install mariadb-operator mariadb-operator/mariadb-operator \
  --namespace mariadb-system \
  --version 0.38.1
```

Skip `0.38.0`.

### 0.38.1 → 25.8.4

```bash
helm upgrade --install mariadb-operator-crds mariadb-operator/mariadb-operator-crds \
  --namespace mariadb-system \
  --version 25.8.4

helm upgrade --install mariadb-operator mariadb-operator/mariadb-operator \
  --namespace mariadb-system \
  --version 25.8.4
```

> [!WARNING]
>
> Patch-by-patch upgrade is **not** required for `25.8.x`. If you are migrating from `0.38.1`, you can jump directly to `25.8.4`.

Confirm Kubernetes version compatibility against the upstream chart metadata before performing the `0.38.1 -> 25.8.4` hop. Do not assume a fixed minimum cluster version from this runbook alone.

If operator pods are stuck in a webhook certificate validation loop, check:

```bash
kubectl get certificate -n mariadb-system
```

If you see `Existing private key is not up to date for spec: [spec.privateKey.algorithm]`, fix it by deleting the secret and webhook deployment:

```bash
kubectl delete secret mariadb-operator-webhook-cert -n mariadb-system
kubectl delete deployment mariadb-operator-webhook -n mariadb-system
```

Then re-run the install script to recreate them.

### 25.8.4 → 25.10.4

```bash
helm upgrade --install mariadb-operator-crds mariadb-operator/mariadb-operator-crds \
  --namespace mariadb-system \
  --version 25.10.4

helm upgrade --install mariadb-operator mariadb-operator/mariadb-operator \
  --namespace mariadb-system \
  --version 25.10.4
```

> [!WARNING]
>
> Patch-by-patch upgrade is **not** required for `25.10.x`.

### 25.10.4 → 26.3.0

```bash
helm upgrade --install mariadb-operator-crds mariadb-operator/mariadb-operator-crds \
  --namespace mariadb-system \
  --version 26.3.0

helm upgrade --install mariadb-operator mariadb-operator/mariadb-operator \
  --namespace mariadb-system \
  --version 26.3.0
```

> [!WARNING]
>
> In the `25.x` replication line, `syncBinlog` changed from **boolean** to **integer**. This affects **Primary/Replica** clusters.
>
> If the existing MariaDB CR still stores `syncBinlog: true`, the newer webhook can reject updates during the `25.10.4 -> 26.3.0` hop. Remove the webhook before patching:
>
> ```bash
> kubectl delete validatingwebhookconfiguration mariadb-operator-webhook
> kubectl -n openstack patch mariadb mariadb-cluster --type merge \
>   -p '{"spec":{"replication":{"syncBinlog":1}}}'
> ```
>
> Then re-run the install script to restore the webhook.

> [!WARNING]
>
> Review the `26.3.0` Helm values schema carefully before upgrading. Several image sections now use structured `repository` plus `tag` values.
>
> Old format:
>
> ```yaml
> config:
>   mariadbImageName: repo/image
> ```
>
> New format:
>
> ```yaml
> config:
>   mariadbImage:
>     repository: repo/image
>     tag: <version>
> ```
>
> Ensure `/etc/genestack/helm-configs/mariadb-operator/mariadb-operator-helm-overrides.yaml` matches the `26.3.0` schema for `maxscaleImage`, `exporterImage`, and `exporterMaxscaleImage` before upgrading.

> [!NOTE]
>
> A new CRD is added with this version: `pointintimerecoveries.k8s.mariadb.com`

## Troubleshooting

### Webhook blocks patches due to old stored values

If the webhook rejects changes because the existing resource in etcd has old-format values such as `syncBinlog: true`, temporarily remove the webhook:

```bash
kubectl scale deployment mariadb-operator -n mariadb-system --replicas=0
kubectl scale deployment mariadb-operator-webhook -n mariadb-system --replicas=0
kubectl delete validatingwebhookconfiguration mariadb-operator-webhook
kubectl delete mutatingwebhookconfiguration mariadb-operator-webhook 2>/dev/null || true
```

Apply the fix, then re-run the install script to restore everything.

### Webhook certificate validation loop

If operator pods are stuck in a `Validating certs` loop, delete the webhook certificate secret and deployment, then re-run the install script:

```bash
kubectl delete secret mariadb-operator-webhook-cert -n mariadb-system
kubectl delete deployment mariadb-operator-webhook -n mariadb-system
/opt/genestack/bin/install-mariadb-operator.sh
```
