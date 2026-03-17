---
title: "Deploy Manila"
weight: 610
---
> [!IMPORTANT]
> **TECH PREVIEW**
>
>

Manila is the Shared File Systems service for OpenStack. Manila provides
coordinated access to shared or distributed file systems.

This document outlines the deployment of OpenStack Manila using Genestack.

The method in which the share is provisioned and consumed is determined
by the Shared File Systems driver, or drivers in the case of a multi-backend
configuration. A variety of available Shared File Systems drivers work with
proprietary backend storage arrays and appliances, open source distributed
file systems, as well as Linux NFS or Samba server.

This tech preview will focus predominantly on the NetApp Clustered
Data ONTAP driver with share server management enabled. The driver interfaces
between OpenStack Manila to NetApp Clustered Data ONTAP storage controllers to
create new storage virtual machines (SVMs) for each tenant share server that is
requested by the Manila service. The driver also creates new data logical interfaces
(LIFs) that provide access for OpenStack tenants on a specific share network to
their shared file systems exported from the share server.

Reference the full online [OpenStack Manila documentation](https://docs.openstack.org/manila/latest/) 

## Create secrets

> [!NOTE]
> **Information about the secrets used**

> [!NOTE]
> **manila-service-keypair is only required for Generic share driver**
>
>
> Manual secret generation is only required if you haven't run the
> `create-secrets.sh` script located in `/opt/genestack/bin`.
>

> [!IMPORTANT]
> **Example secret generation**
>
>
> ``` shell
> kubectl --namespace openstack \
>         create secret generic manila-admin \
>         --type Opaque \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
> kubectl --namespace openstack \
>         create secret generic manila-db-password \
>         --type Opaque \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
> kubectl --namespace openstack \
>         create secret generic manila-rabbitmq-password \
>         --type Opaque \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
> ssh-keygen -qt ed25519 -N '' -C "manila_ssh" -f manila_ssh_key && \
> kubectl --namespace openstack \
>         create secret generic manila-service-keypair \
>         --type Opaque \
>         --from-literal=public_key="$(cat manila_ssh_key.pub)" \
>         --from-literal=private_key="$(cat manila_ssh_key)"
> rm -f manila_ssh_key manila_ssh_key.pub
> ```
>
>

## NetApp Clustered Data ONTAP driver configuration

Manila configuration values for the NetApp ONTAP driver should be edited
for the specific values relevant to the NetApp cluster and the Genestack
environment.

``` yaml
bootstrap:
  enabled: false

conf:
  manila:
    DEFAULT:
      default_share_type: default
      default_share_group_type: default
      enabled_share_backends: netapp_aff_nfs
      enabled_share_protocols: NFS
      osapi_max_limit: 1000
      osapi_share_use_ssl: true
      share_name_template: share-%s
      storage_availability_zone: az1
    netapp_aff_nfs:
      share_backend_name: netapp_aff_nfs
      share_driver: manila.share.drivers.netapp.common.NetAppDriver
      driver_handles_share_servers: true
      driver_ssl_cert_verify: false
      netapp_storage_family: ontap_cluster
      netapp_transport_type: https
      netapp_server_hostname: <cluster_FQDN>
      netapp_server_port: 443
      netapp_login: <admin_user>
      netapp_password: <admin_pass>
      netapp_aggregate_name_search_pattern: ^aggr01_n01_SSD$
      netapp_root_volume_aggregate: aggr01_n01_SSD
      netapp_root_volume: root
      netapp_port_name_search_pattern: ^(a0e-402|a0f-403)$
      netapp_vserver_name_template: mnl_%s
      netapp_lif_name_template: mnl_%(net_allocation_id)s
      netapp_volume_name_template: manila_%(share_id)s
      netapp_enabled_share_protocols: nfs4.1
      netapp_volume_snapshot_reserve_percent: 5
  manila_api_uwsgi:
    uwsgi:
      processes: 4

manifests:
  deployment_share: false
```


## Run the package deployment

> [!IMPORTANT]
> **Run the Manila deployment Script `/opt/genestack/bin/install-manila.sh`**
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
> SERVICE_NAME_DEFAULT="manila"
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
>     # NOTE: The original manila script explicitly used manila-helm-overrides.yaml.
>     # This template includes all .yaml files in the directory like the nova script.
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
>     --set "endpoints.identity.auth.manila.password=$(kubectl --namespace openstack get secret manila-admin -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_db.auth.admin.password=$(kubectl --namespace openstack get secret mariadb -o jsonpath='{.data.root-password}' | base64 -d)"
>     --set "endpoints.oslo_db.auth.manila.password=$(kubectl --namespace openstack get secret manila-db-password -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_cache.auth.memcache_secret_key=$(kubectl --namespace openstack get secret os-memcached -o jsonpath='{.data.memcache_secret_key}' | base64 -d)"
>     --set "conf.manila.keystone_authtoken.memcache_secret_key=$(kubectl --namespace openstack get secret os-memcached -o jsonpath='{.data.memcache_secret_key}' | base64 -d)"
>     --set "endpoints.oslo_messaging.auth.admin.password=$(kubectl --namespace openstack get secret rabbitmq-default-user -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_messaging.auth.manila.password=$(kubectl --namespace openstack get secret manila-rabbitmq-password -o jsonpath='{.data.password}' | base64 -d)"
>     --set "network.ssh.public_key=$(kubectl -n openstack get secret manila-service-keypair -o jsonpath='{.data.public_key}' | base64 -d)"
>     --set "network.ssh.private_key=$(kubectl -n openstack get secret manila-service-keypair -o jsonpath='{.data.private_key}' | base64 -d)"
> )
> 
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
>

> [!TIP]
>
>
> You may need to provide custom values to configure your OpenStack services.
> For a simple single region or lab deployment you can supply an additional
> overrides flag using the example found at
> `base-helm-configs/aio-example-openstack-overrides.yaml`.
>

## Validate functionality

``` shell
kubectl --namespace openstack exec -ti openstack-admin-client -- openstack share service list
```
