---
title: "Deploy Octavia"
weight: 90
---
OpenStack Octavia is the load balancing service within the OpenStack ecosystem, providing scalable and automated load
balancing for cloud applications. Octavia is designed to ensure high availability and reliability by distributing
incoming network traffic across multiple instances of an application, preventing any single instance from becoming a
bottleneck or point of failure. It supports various load balancing algorithms, health monitoring, and SSL termination,
making it a versatile tool for managing traffic within cloud environments. In this document, we will explore the
deployment of OpenStack Octavia using Genestack. By leveraging Genestack, the deployment of Octavia is streamlined,
ensuring that load balancing is seamlessly incorporated into both private and public cloud environments, enhancing
the performance and resilience of cloud applications.

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
>         create secret generic octavia-rabbitmq-password \
>         --type Opaque \
>         --from-literal=username="octavia" \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-64};echo;)"
> kubectl --namespace openstack \
>         create secret generic octavia-db-password \
>         --type Opaque \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
> kubectl --namespace openstack \
>         create secret generic octavia-admin \
>         --type Opaque \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
> kubectl --namespace openstack \
>         create secret generic octavia-certificates \
>         --type Opaque \
>         --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)"
> ```
>
>

## Prerequisite

Before you can deploy octavia, it requires a few things to be setup ahead of time:

* Quota check/update
* Certificate creation
* Security group configuration
* Amphora management network
* Port creation for health manager pods
* Amphora image creation
* and more

In order to automate these tasks, we have provided an ansible role and a playbook. The playbook, `octavia-preconf-main.yaml`,
is located in the ansible/playbook directory. You will need to update the variables in the playbook to match your deployment.

Make sure to udpate the `octavia-preconf-main.yaml` with the correct region, auth url, and password.

> [!TIP]
>
>
> The playbook requires a few pip packages to run properly. While the dependencies for this playbook should be installed by
> default, the playbook runtime can be isolated in a virtualenv if needed.
>

> [!IMPORTANT]
> **Create a virtualenv for running the Octavia pre-deployment playbook**
>
>
> ``` shell
> apt-get install python3-venv python3-pip
> mkdir -p ~/.venvs
> python3 -m venv --system-site-packages ~/.venvs/octavia_preconf
> source .venvs/octavia_preconf/bin/activate
> pip install --upgrade pip
> pip install "ansible>=2.9" "openstacksdk>=1.0.0" "python-openstackclient==6.2.0" kubernetes
> ```
>
>

### Review the role values

The default values are in `/opt/genestack/ansible/playbooks/roles/octavia_preconf/defaults/main.yml`

Review the settings and adjust as necessary. Depending on the size of your cluster, you may want to adjust the
`lb_mgmt_subnet` settings or block icmp and ssh access to the amphora vms.

### Run the playbook

Change to the playbook directory.

``` shell
cd /opt/genestack/ansible/playbooks
```


### Dynamic values


Running the playbook can be fully dynamic by using the following command:

> [!IMPORTANT]
> **Run the playbook with dynamic values**
>
>
> ``` shell
> ansible-playbook /opt/genestack/ansible/playbooks/octavia-preconf-main.yaml \
>                 -e octavia_os_password=$(kubectl get secrets keystone-admin -n openstack -o jsonpath='{.data.password}' | base64 -d) \
>                 -e octavia_os_region_name=$(openstack --os-cloud=default endpoint list --service keystone --interface public -c Region -f value) \
>                 -e octavia_os_auth_url=$(openstack --os-cloud=default endpoint list --service keystone --interface public -c URL -f value) \
>                 -e octavia_helm_file=/tmp/octavia_amphora_provider.yaml
> ```
>
>
>

### Static values skipping tags for post deploy updates


You can get the Keystone url and region with the following command.

``` shell
openstack --os-cloud=default endpoint list --service keystone --interface public -c Region -c URL -f value
```

You can get the admin password by using kubectl.

``` shell
kubectl get secrets keystone-admin -n openstack -o jsonpath='{.data.password}' | base64 -d
```

> [!IMPORTANT]
> **Run the playbook with optional skip-tags values**
>
>
> ``` shell
> ansible-playbook /opt/genestack/ansible/playbooks/octavia-preconf-main.yaml \
>                 -e octavia_os_password=$PASSWORD \
>                 -e octavia_os_region_name=$REGION_NAME \
>                 -e octavia_os_auth_url=$AUTH_URL \
>                 -e octavia_helm_file=/tmp/octavia_amphora_provider.yaml
> ```
>
>
>

### Skipping tags for pre deploy setup


If you have already run the pre-deployment steps and need to re-generate the helm values file, you can skip the
pre-deployment steps by using the `--skip-tags "pre_deploy"` option.

> [!IMPORTANT]
> **Run the playbook with optional skip-tags values**
>
>
> ``` shell
> ansible-playbook /opt/genestack/ansible/playbooks/octavia-preconf-main.yaml \
>                 --skip-tags "pre_deploy"
> ```
>
>

Once everything is complete, a new file will be created in your TMP directory called `/tmp/octavia_amphora_provider.yaml`, this file
contains the necessary information to deploy Octavia via helm. Move this file into the `/etc/genestack/helm-configs/octavia`
directory to have it automatically included when running the Octavia deployment script.

``` shell
mv /tmp/octavia_amphora_provider.yaml /etc/genestack/helm-configs/octavia/
```

## Run the Helm deployment

> [!IMPORTANT]
> **Run the Octavia deployment Script `/opt/genestack/bin/install-octavia.sh`**
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
> SERVICE_NAME_DEFAULT="octavia"
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
> # Set connection string based on whether we use Kube-OVN TLS
> # Source functions library for ensureYq
> source "${GENESTACK_BASE_DIR}/scripts/lib/functions.sh"
> ensureYq
> 
> if helm -n kube-system get values kube-ovn \
>   | yq -e '.networking.ENABLE_SSL == true' >/dev/null 2>&1
> then
>     CONNECTION_STRING="ssl"
> else
>     CONNECTION_STRING="tcp"
> fi
> 
> # Collect all --set arguments, executing commands and quoting safely
> # NOTE: This array contains OpenStack-specific secret retrievals and MUST be updated
> #       with the necessary --set arguments for your target SERVICE_NAME_DEFAULT.
> set_args=(
>     # Keystone endpoint passwords
>     --set "endpoints.identity.auth.admin.password=$(kubectl --namespace openstack get secret keystone-admin -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.identity.auth.octavia.password=$(kubectl --namespace openstack get secret octavia-admin -o jsonpath='{.data.password}' | base64 -d)"
> 
>     # DB passwords
>     --set "endpoints.oslo_db.auth.admin.password=$(kubectl --namespace openstack get secret mariadb -o jsonpath='{.data.root-password}' | base64 -d)"
>     --set "endpoints.oslo_db.auth.octavia.password=$(kubectl --namespace openstack get secret octavia-db-password -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_db_persistence.auth.octavia.password=$(kubectl --namespace openstack get secret octavia-db-password -o jsonpath='{.data.password}' | base64 -d)"
> 
>     # Messaging passwords
>     --set "endpoints.oslo_messaging.auth.admin.password=$(kubectl --namespace openstack get secret rabbitmq-default-user -o jsonpath='{.data.password}' | base64 -d)"
>     --set "endpoints.oslo_messaging.auth.octavia.password=$(kubectl --namespace openstack get secret octavia-rabbitmq-password -o jsonpath='{.data.password}' | base64 -d)"
> 
>     # Memcache secrets
>     --set "endpoints.oslo_cache.auth.memcache_secret_key=$(kubectl --namespace openstack get secret os-memcached -o jsonpath='{.data.memcache_secret_key}' | base64 -d)"
>     --set "conf.octavia.keystone_authtoken.memcache_secret_key=$(kubectl --namespace openstack get secret os-memcached -o jsonpath='{.data.memcache_secret_key}' | base64 -d)"
> 
>     # Certificate passphrase
>     --set "conf.octavia.certificates.ca_private_key_passphrase=$(kubectl --namespace openstack get secret octavia-certificates -o jsonpath='{.data.password}' | base64 -d)"
> 
>     # OVN connections (dynamic clusterIP lookup)
>     --set "conf.octavia.ovn.ovn_nb_connection=$CONNECTION_STRING:$(kubectl --namespace kube-system get service ovn-nb -o jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}')"
>     --set "conf.octavia.ovn.ovn_sb_connection=$CONNECTION_STRING:$(kubectl --namespace kube-system get service ovn-sb -o jsonpath='{.spec.clusterIP}:{.spec.ports[0].port}')"
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
> You may need to provide custom values to configure your openstack services, for a simple single region or lab deployment
> you can supply an additional overrides flag using the example found at `base-helm-configs/aio-example-openstack-overrides.yaml`.
> In other cases such as a multi-region deployment you may want to view the [Multi-Region Support](/operational-guide/multi-region-support/)
> guide to for a workflow solution.
>

## Demo

[![asciicast](https://asciinema.org/a/629814.svg)](https://asciinema.org/a/629814)
