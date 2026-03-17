---
title: "Grafana"
weight: 70
aliases:
  - /grafana/
---

# Grafana

Grafana is installed with the upstream Helm Chart. Running the installation is simple and can be done with our integration script.

Before running the script, you will need to create a secret file with your database username and passwords.

> [!NOTE]
> **Information about the secretes used**
>
>
> Manual secret generation is only required if you haven't run the `create-secrets.sh` script located in `/opt/genestack/bin`.
>
> ??? example "Example secret generation"
>
>     ``` shell
>     kubectl --namespace grafana \
>             create secret generic grafana-db \
>             --type Opaque \
>             --from-literal=password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)" \
>             --from-literal=root-password="$(< /dev/urandom tr -dc _A-Za-z0-9 | head -c${1:-32};echo;)" \
>             --from-literal=username=grafana
>     ```
>

## Custom Values

Before running the deployment script, you must set the `custom_host` value `grafana-helm-overrides.yaml` to the correct FQDN you wish to use within the deployment.

> [!IMPORTANT]
> **grafana-helm-overrides.yaml**
>
>
> ``` yaml
> custom_host: grafana.api.your.domain.tld
> ```
>

## Installation


### Default


The default installation is simple. The `grafana-helm-overrides.yaml` file is located at `/etc/genestack/helm-configs/grafana/` and overrides can be set there to customize the installation.



### Azure Integrated


Before running installation when integrating with Azure AD, you must create te `azure-client-secret`

You can base64 encode your `client_id` and `client_secret` by using the echo and base64 command.

``` shell
echo -n "YOUR CLIENT ID OR SECRET" | base64
```

Apply your base64 encoded values to the `azure-client-secret.yaml` file and apply it to the `grafana` namespace.

> [!IMPORTANT]
> **azure-client-secret.yaml**
>
>
> ``` yaml
> ```yaml
> apiversion: v1
> data:
>   client_id: base64_encoded_client_id
>   client_secret: base64_encoded_client_secret
> kind: secret
> metadata:
>   name: azure-client
>   namespace: grafana
> type: opaque
> ```
> ```
>

Once you have created the secret file, update your `grafana-helm-overrides.yaml` file with the Azure AD values.

> [!IMPORTANT]
> **azure-overrides.yaml**
>
>
> ``` yaml
> ```text
> tenant_id: 122333 # TODO: update this value.  Can be set in CLI.
> 
> extraSecretMounts:
>   - name: azure-client-secret-mount
>     secretName: azure-client
>     defaultMode: 0440
>     mountPath: /etc/secrets/azure-client
>     readOnly: true
>   - name: grafana-db-secret-mount
>     secretName: grafana-db
>     defaultMode: 0440
>     mountPath: /etc/secrets/grafana-db
>     readOnly: true
> 
> grafana.ini:
>   auth.azuread:
>     name: Azure AD
>     enabled: true
>     allow_sign_up: true
>     auto_login: false
>     client_id: $__file{/etc/secrets/azure-client/client_id}
>     client_secret: $__file{/etc/secrets/azure-client/client_secret}
>     scopes: openid email profile
>     auth_url: "https://login.microsoftonline.com/{{ .Values.tenant_id }}/oauth2/v2.0/authorize"
>     token_url: "https://login.microsoftonline.com/{{ .Values.tenant_id }}/oauth2/v2.0/token"
>     allowed_organizations: "{{ .Values.tenant_id }}"
>     role_attribute_strict: false
>     allow_assign_grafana_admin: false
>     skip_org_role_sync: false
>     use_pkce: true
> ```
> ```
>
>

### Listeners and Routes

Listeners and Routes should have been configureed when you installed the Gateway API.  If so some reason they were not created, please following the install guide here: [Gateway API](/deployment-guide/infrastructure-gateway-api/)

### Deployment

Run the Grafana deployment Script `/opt/genestack/bin/install-grafana.sh`

> [!IMPORTANT]
> **Run the Grafana deployment Script `/opt/genestack/bin/install-grafana.sh`**
>
>
> ``` shell
> ```shell
> #!/bin/bash
> # Description: Fetches the version for SERVICE_NAME_DEFAULT from the specified
> # YAML file and executes a helm upgrade/install command with dynamic values files.
> 
> # Disable SC2124 (unused array), SC2145 (array expansion issue), SC2294 (eval)
> # shellcheck disable=SC2124,SC2145,SC2294
> 
> # Service
> SERVICE_NAME_DEFAULT="grafana"
> SERVICE_NAMESPACE="grafana"
> 
> # Helm
> HELM_REPO_NAME_DEFAULT="grafana"
> HELM_REPO_URL_DEFAULT="https://grafana.github.io/helm-charts"
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
> # Collect all --set arguments (empty for Grafana in the original script)
> set_args=()
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
> "${helm_command[@]}"> ```
> ```

