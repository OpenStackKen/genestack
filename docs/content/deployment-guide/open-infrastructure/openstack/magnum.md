---
title: "Magnum"
weight: 100
---
OpenStack Magnum is the container orchestration service within the OpenStack ecosystem, designed to provide an easy-to-use interface for deploying and managing container clusters, such as Kubernetes. Magnum enables cloud users to harness the power of containerization by allowing them to create and manage container clusters as first-class resources within the OpenStack environment. This service integrates seamlessly with other OpenStack components, enabling containers to take full advantage of OpenStack’s networking, storage, and compute capabilities. In this document, we will outline the deployment of OpenStack Magnum using Genestac. By utilizing Genestack, the deployment of Magnum is streamlined, allowing organizations to efficiently manage and scale containerized applications alongside traditional virtual machine workloads within their cloud infrastructure.

> [!NOTE]
>
>
> Before Magnum can be deployed, you must setup and deploy [Barbican](/deployment-guide/open-infrastructure/openstack/barbican/) first.
>

## Create secrets

> [!NOTE]
> **Information about the secrets used**
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
>         create secret generic magnum-rabbitmq-password \
>         --type Opaque \
>         --from-literal=username="magnum" \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-64};echo;)"
> kubectl --namespace openstack \
>         create secret generic magnum-db-password \
>         --type Opaque \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
> kubectl --namespace openstack \
>         create secret generic magnum-admin \
>         --type Opaque \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
> ```
>
>

## Run the package deployment

> [!IMPORTANT]
> **Run the Magnum deployment Script `/opt/genestack/bin/install-magnum.sh`**
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
> SERVICE_NAME_DEFAULT="magnum"
> SERVICE_NAMESPACE="openstack"
> 
> # Helm
> HELM_REPO_NAME_DEFAULT="openstack-helm"
> HELM_REPO_URL_DEFAULT="https://tarballs.opendev.org/openstack/openstack-helm"
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
> # Load chart metadata from custom override YAML if defined
> for yaml_file in "${SERVICE_CUSTOM_OVERRIDES}"/*.yaml; do
>     if [ -f "$yaml_file" ]; then
>         HELM_REPO_URL=$(yq eval '.chart.repo_url // ""' "$yaml_file")
>         HELM_REPO_NAME=$(yq eval '.chart.repo_name // ""' "$yaml_file")
>         SERVICE_NAME=$(yq eval '.chart.service_name // ""' "$yaml_file")
>         break  # use the first match and stop
>     fi
> done
> 
> # Fallback to defaults if variables not set
> : "${HELM_REPO_URL:=$HELM_REPO_URL_DEFAULT}"
> : "${HELM_REPO_NAME:=$HELM_REPO_NAME_DEFAULT}"
> : "${SERVICE_NAME:=$SERVICE_NAME_DEFAULT}"
> 
> 
> # Determine Helm chart path
> if [[ "$HELM_REPO_URL" == oci://* ]]; then
>     # OCI registry path
>     HELM_CHART_PATH="$HELM_REPO_URL/$HELM_REPO_NAME/$SERVICE_NAME"
> else
>     # --- Helm Repository and Execution ---
>     helm repo add "$HELM_REPO_NAME" "$HELM_REPO_URL"
>     helm repo update
>     HELM_CHART_PATH="$HELM_REPO_NAME/$SERVICE_NAME"
> fi
> 
> # Debug output
> echo "[DEBUG] HELM_REPO_URL=$HELM_REPO_URL"
> echo "[DEBUG] HELM_REPO_NAME=$HELM_REPO_NAME"
> echo "[DEBUG] SERVICE_NAME=$SERVICE_NAME"
> echo "[DEBUG] HELM_CHART_PATH=$HELM_CHART_PATH"
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
> # Include all YAML files from the GLOBAL configuration directory
> # NOTE: Files here override base settings and are applied before service-specific ones.
> if [[ -d "$GLOBAL_OVERRIDES_DIR" ]]; then
>     echo "Including global overrides from directory: $GLOBAL_OVERRIDES_DIR"
>     for file in "$GLOBAL_OVERRIDES_DIR"/*.yaml; do
>         if [[ -e "$file" ]]; then
>             echo " - $file"
>             overrides_args+=("-f" "$file")
>         fi
>     done
> else
>     echo "Warning: Global override directory not found: $GLOBAL_OVERRIDES_DIR"
> fi
> 
> # Include all YAML files from the custom SERVICE configuration directory
> # NOTE: Files here have the highest precedence.
> if [[ -d "$SERVICE_CUSTOM_OVERRIDES" ]]; then
>     echo "Including overrides from service config directory:"
>     for file in "$SERVICE_CUSTOM_OVERRIDES"/*.yaml; do
>         if [[ -e "$file" ]]; then
>             echo " - $file"
>             overrides_args+=("-f" "$file")
>         fi
>     done
> else
>     echo "Warning: Service config directory not found: $SERVICE_CUSTOM_OVERRIDES"
> fi
> 
> echo
> 
> # Collect all --set arguments, executing commands and quoting safely
> set_args=(
>     --set "endpoints.identity.auth.admin.password=$(kubectl --namespace openstack get secret keystone-admin -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.identity.auth.magnum.password=$(kubectl --namespace openstack get secret magnum-admin -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_db.auth.admin.password=$(kubectl --namespace openstack get secret mariadb -o jsonpath='{.data.root-password}' | base64 -d)"
>     --set "endpoints.oslo_db.auth.magnum.password=$(kubectl --namespace openstack get secret magnum-db-password -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_messaging.auth.admin.password=$(kubectl --namespace openstack get secret rabbitmq-default-user -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_messaging.auth.magnum.password=$(kubectl --namespace openstack get secret magnum-rabbitmq-password -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_cache.auth.memcache_secret_key=$(kubectl --namespace openstack get secret os-memcached -o jsonpath='{.data.memcache_secret_key}' | base64 -d)"
>     --set "conf.magnum.keystone_authtoken.memcache_secret_key=$(kubectl --namespace openstack get secret os-memcached -o jsonpath='{.data.memcache_secret_key}' | base64 -d)"
> )
> 
> helm_command=(
>     helm upgrade --install "$SERVICE_NAME_DEFAULT" "$HELM_CHART_PATH"
>     --version "${SERVICE_VERSION}"
>     --namespace="$SERVICE_NAMESPACE"
>     --timeout 120m
>     --create-namespace
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
> ```
>

> [!TIP]
>
>
> You may need to provide custom values to configure your openstack services, for a simple single region or lab deployment you can supply an additional overrides flag using the example found at `base-helm-configs/aio-example-openstack-overrides.yaml`.
> In other cases such as a multi-region deployment you may want to view the [Multi-Region Support](/operational-guide/multi-region-support/) guide to for a workflow solution.
>

## Validate functionality

``` shell
kubectl --namespace openstack exec -ti openstack-admin-client -- openstack coe cluster list
```

## Create a Public ClusterTemplate

User must have the admin role to create the public ClusterTemplate. For instructions on creating and using it to deploy a new Kubernetes cluster, please refer to the ClusterTemplate section in the [Magnum Kubernetes Cluster Setup Guide](https://docs.rackspacecloud.com/magnum-kubernetes-cluster-setup-guide/#clustertemplate).


## Deploying Magnum with Cluster API (CAPI) Driver

Magnum can use CAPI as the backend driver to spin up k8s clusters. Magnum CAPI Helm is one of the projects that provides an OpenStack Magnum driver which uses Helm to create the clustr with CAPI. The documentation below assume you are using magnum-capi-helm as your CAPI driver. Diver can be found [here.](https://opendev.org/openstack/magnum-capi-helm)

![CAPI Architecture](/assets/images/capi-architecture.png)


### Prerequisites

Before deploying magnum with the CAPI Driver:

1. Ensure your magnum image has the magnum-capi-helm driver installed. See our [Magnum Containerfile.](https://github.com/rackerlabs/genestack-images/blob/main/ContainerFiles/magnum)
2. Ensure your magnum image has helm installed. See our [Magnum Containerfile.](https://github.com/rackerlabs/genestack-images/blob/main/ContainerFiles/magnum)
3. Ensure you are using magnum helm version 2025.1 or above, as CAPI functionality was added on openstack-helm during this release.
4. You will need a management cluster for CAPI. See [How CAPI Works](https://cluster-api.sigs.k8s.io) with mgt cluster to spin up worker nodes.
5. On your management cluster make sure you install cluster-addon. It is found [here.](https://github.com/azimuth-cloud/cluster-api-addon-provider)

### Magnum Helm Config

In order to switch to CAPI we need to make sure that magnum has the right config passed to it. Here is an example we can use:

```
conf:
  capi:
    enabled: true
    clusterName: k8s-managment-cluster
    apiServer: https://127.0.0.1:6443
    certificateAuthorityData: < k8s-managment-cluster CA Data > 
    contextName: k8s-management
    userName: admin@k8s-management
    clientCertificateData: < k8s-managment-cluster clientCert Data > 
    clientKeyData: < k8s-managment-cluster clientKey Data >
  magnum:
    capi_helm:
      kubeconfig_file: /etc/magnum/kubeconfig.conf
    barbican_client:
      endpoint_type: publicURL
      region_name: RegionOne
    cinder_client:
      endpoint_type: publicURL
      region_name: RegionOne
   ... 
```

First, make sure the capi section has the management cluster kubeconfig file content. This will be used by magnum to talk to managment cluster.
Next, under magnum add the capi_helm config to point to where we find the kubeconfig file. This is usually at `/etc/magnum/kubeconfig.con`.
Additionally we can make the driver point to specific helm charts. This is useful if you have made changes specific to your environment to the chart
and would like to use that. This can be done like so:

```
magnum:
    capi_helm:
      kubeconfig_file: /etc/magnum/kubeconfig.conf
      helm_chart_repo: https://rackerlabs.github.io/genestack-capi-helm-charts
      default_helm_chart_version: 0.1.0
```
