---
title: "Glance"
description: "OpenStack image service."
weight: 30
---

[Glance](https://docs.openstack.org/glance/latest/) is the image service within the OpenStack ecosystem, responsible for discovering, registering, and retrieving virtual machine images. Glance provides a centralized repository where users can store and manage a wide variety of VM images, ranging from standard operating system snapshots to custom machine images tailored for specific workloads. This service plays a crucial role in enabling rapid provisioning of instances by providing readily accessible, pre-configured images that can be deployed across the cloud. 

This section will outline the deployment of OpenStack Glance using Genestack. The deployment process is streamlined, ensuring Glance is robustly integrated with other OpenStack services to deliver seamless image management and retrieval.

## Create secrets

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
>         create secret generic glance-rabbitmq-password \
>         --type Opaque \
>         --from-literal=username="glance" \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-64};echo;)"
> kubectl --namespace openstack \
>         create secret generic glance-db-password \
>         --type Opaque \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
> kubectl --namespace openstack \
>         create secret generic glance-admin \
>         --type Opaque \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
> ```
>
>

> [!NOTE]
>
>
> Before running the Glance deployment you should configure the backend which is defined in the `helm-configs/glance/glance-helm-overrides.yaml` file. The default is a making the assumption we're running with Ceph deployed by Rook so the backend is configured to be cephfs with multi-attach functionality. While this works great, you should consider all of the available storage backends and make the right decision for your environment.
> Recent Glance releases validate uploaded/imported image content against the declared `disk_format` by default. Ensure image pipelines set `--disk-format` correctly, or tune `conf.glance.image_format.require_image_format_match` and `conf.glance.image_format.gpt_safety_checks_nonfatal` in your overrides.
>

## Define policy configuration

> [!NOTE]
> **Information about the default policy rules used**
>
>
> The default policy allows only the **glance_admin** role to publicize images. The default policy allows only the **glance_admin** role or
> **owner** role to download images. These default policy roles are found in genestack/base-helm-configs/glance/glance-helm-overrides.yaml.
> To modify these policies, follow the policy allow concepts in the "Policy change to allow admin or owner to publicize image" example.
>

> [!IMPORTANT]
> **Default policy rules**
>
>
> ``` yaml
> conf:
>   policy:
>     "admin_required": "role:admin or role:glance_admin"
>     "default": "role:admin or role:glance_admin"
>     "context_is_admin": "role:admin or role:glance_admin"
>     "publicize_image": "role:glance_admin"
>     "is_owner": "tenant:%(owner)s"
>     "download_image": "rule:is_owner or rule:context_is_admin"
> ```
>

> [!IMPORTANT]
> **Policy change to allow admin or owner to publicize image**
>
>
> ``` yaml
> conf:
>   policy:
>     "admin_required": "role:admin or role:glance_admin"
>     "default": "role:admin or role:glance_admin"
>     "context_is_admin": "role:admin or role:glance_admin"
>     "is_owner": "tenant:%(owner)s"
>     "publicize_image": "rule:context_is_admin or role:is_owner"
>     "download_image": "rule:is_owner or rule:context_is_admin"
> ```
>

> To assign the **glance_admin** role to a user, you can use the OpenStack CLI or dashboard. For example, using the OpenStack CLI:
>
> ``` shell
> openstack role add --project <project_name> --user <user_name> glance_admin
> ```
>

## Run the package deployment

> [!IMPORTANT]
> **Run the Glance deployment Script `/opt/genestack/bin/install-glance.sh`**
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
> SERVICE_NAME_DEFAULT="glance"
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
> # NOTE: This array contains OpenStack-specific secret retrievals and MUST be updated
> #       with the necessary --set arguments for your target SERVICE_NAME_DEFAULT.
> set_args=(
>     --set "endpoints.identity.auth.admin.password=$(kubectl --namespace openstack get secret keystone-admin -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.identity.auth.glance.password=$(kubectl --namespace openstack get secret glance-admin -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_db.auth.admin.password=$(kubectl --namespace openstack get secret mariadb -o jsonpath='{.data.root-password}' | base64 -d)"
>     --set "endpoints.oslo_db.auth.glance.password=$(kubectl --namespace openstack get secret glance-db-password -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_cache.auth.memcache_secret_key=$(kubectl --namespace openstack get secret os-memcached -o jsonpath='{.data.memcache_secret_key}' | base64 -d)"
>     --set "conf.glance.keystone_authtoken.memcache_secret_key=$(kubectl --namespace openstack get secret os-memcached -o jsonpath='{.data.memcache_secret_key}' | base64 -d)"
>     --set "endpoints.oslo_messaging.auth.admin.password=$(kubectl --namespace openstack get secret rabbitmq-default-user -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_messaging.auth.glance.password=$(kubectl --namespace openstack get secret glance-rabbitmq-password -o jsonpath='{.data.password}' | base64 -d)"
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
> ```
>

> [!TIP]
>
>
> You may need to provide custom values to configure your openstack services, for a simple single region or lab deployment you can supply an additional overrides flag using the example found at `base-helm-configs/aio-example-openstack-overrides.yaml`.
> In other cases such as a multi-region deployment you may want to view the [Multi-Region Support](/operational-guide/multi-region-support/) guide to for a workflow solution.
>

> [!NOTE]
>
>
> The defaults disable `storage_init` because we're using **pvc** as the image backend type. In production this should be changed to swift.
>

## Validate functionality

``` shell
kubectl --namespace openstack exec -ti openstack-admin-client -- openstack image list
```

> [!IMPORTANT]
> **External Image Store**
>
>
> If glance will be deployed with an external swift storage backend, review the
> [OpenStack Glance Swift Store](/operational-guide/openstack-glance-swift-store/) or the
> [OpenStack Glance External Ceph Store](/operational-guide/openstack-glance-ceph-store/) operator
> documentation for additional steps and setup.
>

## Demo

[![asciicast](https://asciinema.org/a/629806.svg)](https://asciinema.org/a/629806)
