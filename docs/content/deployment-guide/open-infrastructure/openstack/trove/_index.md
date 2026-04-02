---
title: "Trove"
weight: 170
type: docs
simple_list: true
description: "OpenStack database as a Service (DBaaS)."
cascade:
  - type: docs
---

[Trove](https://docs.openstack.org/trove/latest/) is the Database as a Service (DBaaS) component of the OpenStack cloud computing platform, providing scalable and reliable database provisioning and management capabilities. It enables users to deploy, manage, and scale database instances without the complexity of manual database administration. This document details the deployment of OpenStack Trove within Genestack.

> [!GENESTACK]
>
> Genestack facilitates the deployment process by leveraging Kubernetes' orchestration capabilities, ensuring seamless integration and management of Trove services across different database engines and environments.

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
>         create secret generic trove-rabbitmq-password \
>         --type Opaque \
>         --from-literal=username="trove" \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-64};echo;)"
> kubectl --namespace openstack \
>         create secret generic trove-db-password \
>         --type Opaque \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
> kubectl --namespace openstack \
>         create secret generic trove-admin \
>         --type Opaque \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
> ```
>
>

## Define policy configuration

> [!NOTE]
> **Information about the default policy rules used**
>
>
> The default RabbitMQ policy sets quorum queues target group size to 3 for
> the `trove` vhost. This can be changed in `base-kustomize/trove/base/policies.yaml`.
>

> [!IMPORTANT]
> **Default RabbitMQ policy**
>
>
> ``` yaml
> apiVersion: rabbitmq.com/v1beta1
> kind: Policy
> metadata:
>   name: trove-quorum-three-replicas
>   namespace: openstack
> spec:
>   name: trove-quorum-three-replicas
>   vhost: "trove"
>   pattern: ".*"
>   applyTo: queues
>   definition:
>     target-group-size: 3
>   priority: 0
>   rabbitmqClusterReference:
>     name: rabbitmq
> ```
>
>

## Run the package deployment

> [!IMPORTANT]
> **Run the Trove deployment Script `/opt/genestack/bin/install-trove.sh`**
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
> SERVICE_NAME_DEFAULT="trove"
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
>     --set "endpoints.identity.auth.trove.password=$(kubectl --namespace openstack get secret trove-admin -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.identity.auth.nova.password=$(kubectl --namespace openstack get secret nova-admin -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.identity.auth.neutron.password=$(kubectl --namespace openstack get secret neutron-admin -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.identity.auth.cinder.password=$(kubectl --namespace openstack get secret cinder-admin -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_db.auth.admin.password=$(kubectl --namespace openstack get secret mariadb -o jsonpath='{.data.root-password}' | base64 -d)"
>     --set "endpoints.oslo_db.auth.trove.password=$(kubectl --namespace openstack get secret trove-db-password -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_cache.auth.memcache_secret_key=$(kubectl --namespace openstack get secret os-memcached -o jsonpath='{.data.memcache_secret_key}' | base64 -d)"
>     --set "conf.trove.keystone_authtoken.memcache_secret_key=$(kubectl --namespace openstack get secret os-memcached -o jsonpath='{.data.memcache_secret_key}' | base64 -d)"
>     --set "conf.trove.database.slave_connection=mysql+pymysql://trove:$(kubectl --namespace openstack get secret trove-db-password -o jsonpath='{.data.password}' | base64 -d)@mariadb-cluster-secondary.openstack.svc.cluster.local:3306/trove"
>     --set "endpoints.oslo_messaging.auth.admin.password=$(kubectl --namespace openstack get secret rabbitmq-default-user -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_messaging.auth.trove.password=$(kubectl --namespace openstack get secret trove-rabbitmq-password -o jsonpath='{.data.password}' | base64 -d)"
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
>

> [!TIP]
>
>
> You may need to provide custom values to configure your openstack services, for a simple single region or lab deployment you can supply an additional overrides flag using the example found at `base-helm-configs/aio-example-openstack-overrides.yaml`.
> In other cases such as a multi-region deployment you may want to view the [Multi-Region Support](/operational-guide/multi-region-support/) guide to for a workflow solution.
>

## Validate the Deployment

After deployment, verify that Trove services are running:

``` shell
kubectl --namespace openstack get pods -l application=trove
```

Check the Trove API endpoint:

``` shell
openstack database service list
```

## Database Instance Management

### Create a Database Instance

``` shell
openstack database instance create my-database \
    --flavor <flavor-id> \
    --size 10 \
    --datastore mysql \
    --datastore-version 5.7 \
    --nic net-id=<network-id>
```

### List Database Instances

``` shell
openstack database instance list
```

### Show Database Instance Details

``` shell
openstack database instance show my-database
```

### Create Database and Users

``` shell
# Create a database
openstack database db create my-database myapp_db

# Create a user with access to the database
openstack database user create my-database myapp_user myapp_password --databases myapp_db

# List databases
openstack database db list my-database

# List users
openstack database user list my-database
```

## Supported Datastores

Trove supports multiple database engines including:

- MySQL
- MariaDB
- PostgreSQL
- MongoDB
- Redis
- Cassandra

Configure datastore images and versions according to your requirements in the Helm overrides.

## Database Images

Before using Trove, you need to build and upload database images. For MySQL:

### Build MySQL 8.4 Image

``` shell
# Build and upload MySQL 8.4 image
/opt/genestack/scripts/build-trove-mysql-image.sh
```

### Configure Datastores

``` shell
# Setup MySQL datastores and versions
/opt/genestack/scripts/setup-trove-datastores.sh
```

For detailed instructions on building database images, see the [MySQL Images Guide](/deployment-guide/open-infrastructure/openstack/trove/trove-mysql-images/).

## Troubleshooting

### Check Trove Logs

``` shell
# API logs
kubectl --namespace openstack logs -l application=trove,component=api

# Conductor logs
kubectl --namespace openstack logs -l application=trove,component=conductor

# Taskmanager logs
kubectl --namespace openstack logs -l application=trove,component=taskmanager
```

### Common Issues

1. **Database instance creation fails**: Ensure that Nova, Neutron, and Cinder are properly configured and accessible
2. **Guest agent communication issues**: Verify network connectivity between Trove and database instances
3. **Image not found**: Ensure datastore images are properly uploaded to Glance

## Configuration Options

Key configuration options in `trove-helm-overrides.yaml`:

- `conf.trove.DEFAULT.default_datastore`: Default database engine
- `conf.trove.DEFAULT.management_networks`: Management network for guest instances
- `conf.trove.DEFAULT.network_driver`: Network driver configuration
- `pod.resources`: Resource requests and limits for Trove components

For advanced configuration, refer to the [OpenStack Trove documentation](https://docs.openstack.org/trove/latest/).

