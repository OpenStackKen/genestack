---
title: "Deploy the MariaDB Operator and Mariadb Cluster"
weight: 150
---
## Create secret

> [!NOTE]
> **Information about the secretes used**
>
>
> Manual secret generation is only required if you haven't run the `create-secrets.sh` script located in `/opt/genestack/bin`.
>

> [!IMPORTANT]
> **Example secret generation**
>
>
> ``` shell
> kubectl --namespace openstack \
>         create secret generic mariadb \
>         --type Opaque \
>         --from-literal=root-password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)" \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
> ```
>
>

## Deploy the mariadb operator

```
CLUSTER_NAME=`kubectl config view --minify -o jsonpath='{.clusters[0].name}'`
echo $CLUSTER_NAME
```

If `cluster_name` was anything other than `cluster.local` you should pass that as a parameter to the installer

> [!IMPORTANT]
> **Run the mariadb-operator deployment Script `/opt/genestack/bin/install-mariadb-operator.sh` You can include cluster_name paramater from the output of $CLUSTER_NAME. If no paramaters are provided, the system will deploy with `cluster.local` as the cluster name.**
>
>
> ``` shell
> #!/bin/bash
> # Description: Fetches the version for SERVICE_NAME_DEFAULT from the specified
> # YAML file and executes a helm upgrade/install command with dynamic values files.
> 
> # Disable SC2124 (unused array), SC2145 (array expansion issue), SC2294 (eval)
> # shellcheck disable=SC2124,SC2145,SC2294
> 
> # Service
> SERVICE_NAME_DEFAULT="mariadb-operator"
> CRDS_NAME_DEFAULT="mariadb-operator-crds"
> SERVICE_NAMESPACE="mariadb-system"
> 
> # Helm
> HELM_REPO_NAME_DEFAULT="mariadb-operator"
> HELM_REPO_URL_DEFAULT="https://helm.mariadb.com/mariadb-operator"
> 
> # Base directories provided by the environment
> GENESTACK_BASE_DIR="${GENESTACK_BASE_DIR:-/opt/genestack}"
> GENESTACK_OVERRIDES_DIR="${GENESTACK_OVERRIDES_DIR:-/etc/genestack}"
> 
> # Define service-specific override directories based on the framework
> SERVICE_BASE_OVERRIDES="${GENESTACK_BASE_DIR}/base-helm-configs/${SERVICE_NAME_DEFAULT}"
> SERVICE_CUSTOM_OVERRIDES="${GENESTACK_OVERRIDES_DIR}/helm-configs/${SERVICE_NAME_DEFAULT}"
> 
> # Define the Global Overrides directory used in the original script
> GLOBAL_OVERRIDES_DIR="${GENESTACK_OVERRIDES_DIR}/helm-configs/global_overrides"
> 
> # Read the desired chart version from VERSION_FILE
> VERSION_FILE="${GENESTACK_OVERRIDES_DIR}/helm-chart-versions.yaml"
> 
> if [ ! -f "$VERSION_FILE" ]; then
>     echo "Error: helm-chart-versions.yaml not found at $VERSION_FILE" >&2
>     exit 1
> fi
> 
> # Extract version dynamically using the SERVICE_NAME_DEFAULT variable
> SERVICE_VERSION=$(grep "^[[:space:]]*${SERVICE_NAME_DEFAULT}:" "$VERSION_FILE" | sed "s/.*${SERVICE_NAME_DEFAULT}: *//")
> 
> if [ -z "$SERVICE_VERSION" ]; then
>     echo "Error: Could not extract version for '$SERVICE_NAME_DEFAULT' from $VERSION_FILE" >&2
>     exit 1
> fi
> 
> echo "Found version for $SERVICE_NAME_DEFAULT: $SERVICE_VERSION"
> 
> # Default parameter value
> export CLUSTER_NAME=${CLUSTER_NAME:-cluster.local}
> 
> # 'cluster.local' is the default value in base helm values file
> if [ "${CLUSTER_NAME}" != "cluster.local" ]; then
>     SERVICE_CONFIG_FILE="$SERVICE_CUSTOM_OVERRIDES/mariadb-operator-helm-overrides.yaml"
>     touch "$SERVICE_CONFIG_FILE"
>     # Check if the file is empty and add/modify content accordingly
>     if [ ! -s "$SERVICE_CONFIG_FILE" ]; then
>         echo "clusterName: $CLUSTER_NAME" > "$SERVICE_CONFIG_FILE"
>     else
>         # If the clusterName line exists, modify it, otherwise add it at the end
>         if grep -q "^clusterName:" "$SERVICE_CONFIG_FILE"; then
>             sed -i -e "s/^clusterName: .*/clusterName: ${CLUSTER_NAME}/" "$SERVICE_CONFIG_FILE"
>         else
>             echo "clusterName: $CLUSTER_NAME" >> "$SERVICE_CONFIG_FILE"
>         fi
>     fi
> fi
> 
> # Load chart metadata from custom override YAML if defined
> for yaml_file in "${SERVICE_CUSTOM_OVERRIDES}"/*.yaml; do
>     if [ -f "$yaml_file" ]; then
>         HELM_REPO_URL=$(yq eval '.chart.repo_url // ""' "$yaml_file")
>         HELM_REPO_NAME=$(yq eval '.chart.repo_name // ""' "$yaml_file")
>         SERVICE_NAME=$(yq eval '.chart.service_name // ""' "$yaml_file")
>         CRDS_NAME=$(yq eval '.chart.service_crds // ""' "$yaml_file")
>         break  # use the first match and stop
>     fi
> done
> 
> # Fallback to defaults if variables not set
> : "${HELM_REPO_URL:=$HELM_REPO_URL_DEFAULT}"
> : "${HELM_REPO_NAME:=$HELM_REPO_NAME_DEFAULT}"
> : "${SERVICE_NAME:=$SERVICE_NAME_DEFAULT}"
> : "${CRDS_NAME:=$CRDS_NAME_DEFAULT}"
> 
> 
> # Determine Helm chart path
> if [[ "$HELM_REPO_URL" == oci://* ]]; then
>     # OCI registry path
>     CRDS_CHART_PATH="$HELM_REPO_URL/$HELM_REPO_NAME/$CRDS_NAME"
>     HELM_CHART_PATH="$HELM_REPO_URL/$HELM_REPO_NAME/$SERVICE_NAME"
> else
>     # --- Helm Repository and Execution ---
>     helm repo add "$HELM_REPO_NAME" "$HELM_REPO_URL"
>     helm repo update
>     CRDS_CHART_PATH="$HELM_REPO_NAME/$CRDS_NAME"
>     HELM_CHART_PATH="$HELM_REPO_NAME/$SERVICE_NAME"
> fi
> 
> # Debug output
> echo "[DEBUG] HELM_REPO_URL=$HELM_REPO_URL"
> echo "[DEBUG] HELM_REPO_NAME=$HELM_REPO_NAME"
> echo "[DEBUG] SERVICE_NAME=$SERVICE_NAME"
> echo "[DEBUG] CRDS_NAME=$CRDS_NAME"
> echo "[DEBUG] HELM_CHART_PATH=$HELM_CHART_PATH"
> echo "[DEBUG] CRDS_CHART_PATH=$CRDS_CHART_PATH"
> 
> # Prepare an array to collect -f arguments
> overrides_args=()
> 
> # Include all YAML files from the BASE configuration directory
> # NOTE: Files in this directory are included first.
> if [[ -d "$SERVICE_BASE_OVERRIDES" ]]; then
>     echo "Including base overrides from directory: $SERVICE_BASE_OVERRIDES"
>     for file in "$SERVICE_BASE_OVERRIDES"/*.yaml; do
>         # Check that there is at least one match
>         if [[ -e "$file" ]]; then
>             echo " - $file"
>             overrides_args+=("-f" "$file")
>         fi
>     done
> else
>     echo "Warning: Base override directory not found: $SERVICE_BASE_OVERRIDES"
> fi
> 
> # Include all YAML files from the custom SERVICE configuration directory
> # NOTE: Files here have the highest precedence.
> if [[ -d "$SERVICE_CUSTOM_OVERRIDES" ]]; then
>     echo "Including overrides from service config directory: $SERVICE_CUSTOM_OVERRIDES"
>     for file in "$SERVICE_CUSTOM_OVERRIDES"/*.yaml; do
>         if [[ -e "$file" ]]; then
>             echo " - $file"
>             overrides_args+=("-f" "$file")
>         fi
>     done
> else
>     echo "Warning: Service overrides directory not found: $SERVICE_CUSTOM_OVERRIDES"
> fi
> 
> echo
> 
> # Collect all --set arguments, executing commands and quoting safely
> set_args=()
> 
> # Install the CRDs that match the version defined
> helm upgrade --install --namespace="$SERVICE_NAMESPACE" --create-namespace "$CRDS_NAME_DEFAULT" "$CRDS_CHART_PATH" --version "${SERVICE_VERSION}"
> 
> helm_command=(
>     helm upgrade --install "$SERVICE_NAME_DEFAULT" "$HELM_CHART_PATH"
>     --version "${SERVICE_VERSION}"
>     --namespace="$SERVICE_NAMESPACE"
>     --timeout 120m
> 
>     "${overrides_args[@]}"
>     "${set_args[@]}"
> 
>     # Post-renderer configuration
>     --post-renderer "$GENESTACK_OVERRIDES_DIR/kustomize/kustomize.sh"
>     --post-renderer-args "$SERVICE_NAME_DEFAULT/overlay"
> 
>     "$@"
> )
> 
> echo "Executing Helm command (arguments are quoted safely):"
> printf '%q ' "${helm_command[@]}"
> echo
> 
> # Execute the command directly from the array
> "${helm_command[@]}"
> ```
>

> [!NOTE]
>
>
> The operator may take a minute to get ready, before deploying the Galera cluster, wait until the webhook is online.
>

``` shell
kubectl --namespace mariadb-system get pods -w
```

## Deploy the MariaDB Cluster

> [!NOTE]
>
>
> MariaDB has a base configuration which is HA and production ready. If you're deploying on a small cluster the `aio` configuration may better suit the needs of the environment.
>
>

### Replication _(Recommended)_


Replication in MariaDB involves synchronizing data between a primary database and one or more replicas, enabling continuous data availability even in the event of hardware failures or outages. By using MariaDB replication, OpenStack deployments can achieve improved fault tolerance and load balancing, ensuring that critical cloud services remain operational and performant at all times.

``` shell
kubectl --namespace openstack apply -k /etc/genestack/kustomize/mariadb-cluster/overlay
```



### Galera


MariaDB with Galera Cluster is a popular choice for ensuring high availability and scalability in OpenStack deployments. Galera is a synchronous multi-master replication plugin for MariaDB, allowing all nodes in the cluster to read and write simultaneously while ensuring data consistency across the entire cluster. This setup is particularly advantageous in OpenStack environments, where database operations must be highly reliable and available to support the various services that depend on them. By using Galera with MariaDB, OpenStack deployments can achieve near-instantaneous replication across multiple nodes, enhancing fault tolerance and providing a robust solution for handling the high-demand workloads typical in cloud environments.

``` shell
kubectl --namespace openstack apply -k /etc/genestack/kustomize/mariadb-cluster/galera
```



### AIO


In some OpenStack deployments, a single MariaDB server is used to manage the database needs of the cloud environment. While this setup is simpler and easier to manage than clustered solutions, it is typically suited for smaller environments or use cases where high availability and fault tolerance are not critical. A single MariaDB server provides a centralized database service for storing and managing the operational data of OpenStack components, ensuring consistent performance and straightforward management. However, it is important to recognize that this configuration presents a single point of failure, making it less resilient to outages or hardware failures compared to more robust, multi-node setups.

``` shell
kubectl --namespace openstack apply -k /etc/genestack/kustomize/mariadb-cluster/aio
```


## Verify readiness with the following command

``` shell
kubectl --namespace openstack get mariadbs -w
```
