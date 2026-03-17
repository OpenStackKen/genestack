---
title: "Setup the MetalLB Loadbalancer"
weight: 170
aliases:
  - /deployment-guide/infrastructure-metallb/
  - /infrastructure-metallb/
---
The MetalLb loadbalancer can be setup by editing the following file `metallb-openstack-service-lb.yml`, You will need to add
your "external" VIP(s) to the loadbalancer so that they can be used within services. These IP addresses are unique and will
need to be customized to meet the needs of your environment.

> [!TIP]
>
>
> When L2Advertisement is used, you should use a CIDR that is not overlapping with any local interface CIDR.
> This also enables later migration to BGP advertisement.
>

## Create the MetalLB namespace

``` shell
kubectl apply -f /etc/genestack/manifests/metallb/metallb-namespace.yaml
```

## Install MetalLB

> [!IMPORTANT]
> **Run the MetalLB deployment Script `/opt/genestack/bin/install-metallb.sh` You can include paramaters to deploy aio or base-monitoring. No paramaters deploys base**
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
> SERVICE_NAME_DEFAULT="metallb"
> SERVICE_NAMESPACE="metallb-system"
> 
> # Helm
> HELM_REPO_NAME_DEFAULT="metallb"
> HELM_REPO_URL_DEFAULT="https://metallb.github.io/metallb"
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
>     # NOTE: Metallb doesn't typically require a post-renderer, but we keep it
>     # for template compliance.
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

## Example LB manifest

> [!NOTE]
> **Example for `metallb-openstack-service-lb.yml` file.**
>
>
> ``` yaml
> ---
> apiVersion: metallb.io/v1beta1
> kind: IPAddressPool
> metadata:
>   name: gateway-api-external
>   namespace: metallb-system
> spec:
>   addresses:
>     - 10.74.8.99/32  # This is assumed to be the public LB vip address
>   autoAssign: false
>   avoidBuggyIPs: true
> ---
> apiVersion: metallb.io/v1beta1
> kind: L2Advertisement
> metadata:
>   name: openstack-external-advertisement
>   namespace: metallb-system
> spec:
>   ipAddressPools:
>     - gateway-api-external
>   nodeSelectors:  # Optional block to limit nodes for a given advertisement
>     - matchLabels:
>         node-role.kubernetes.io/worker: worker
> #  interfaces:  # Optional block to limit ifaces used to advertise VIPs
> #    - br-host
> ---
> apiVersion: metallb.io/v1beta1
> kind: IPAddressPool
> metadata:
>   name: primary
>   namespace: metallb-system
> spec:
>   addresses:
>     - 10.234.0.0/24
>   autoAssign: false
>   avoidBuggyIPs: true
> ---
> apiVersion: metallb.io/v1beta1
> kind: L2Advertisement
> metadata:
>   name: cluster-internal-advertisement
>   namespace: metallb-system
> spec:
>   ipAddressPools:
>     - primary
>   nodeSelectors:  # Optional block to limit nodes for a given advertisement
>     - matchLabels:
>         node-role.kubernetes.io/worker: worker
> #  interfaces:  # Optional block to limit ifaces used to advertise VIPs
> #    - br-host
> ```
>

> [!TIP]
>
>
> Edit the `/etc/genestack/manifests/metallb/metallb-openstack-service-lb.yml` file following the comment instructions with the details of your cluster.
> The file `metallb-openstack-service-lb.yml` is intially provided during bootstrap for genestack.
>

Verify the deployment of MetalLB by checking the pods in the `metallb-system` namespace.

``` shell
kubectl --namespace metallb-system get deployment.apps/metallb-controller
```

Once MetalLB is operatianal, apply the metallb service manifest.

``` shell
kubectl apply -f /etc/genestack/manifests/metallb/metallb-openstack-service-lb.yml
```

## Re-IP the advertisement pools

In situations where the advertisement pools must be changed, the following disruptive procedure can be used:

Update existing metallb configuration:

```shell
kubectl -n metallb-system delete IPAddressPool/primary
kubectl -n metallb-system delete IPAddressPool/gateway-api-external
kubectl apply -f /etc/genestack/manifests/metallb/metallb-openstack-service-lb.yml
```

Restart the metallb controller:

```shell
kubectl rollout restart deployment metallb-controller -n metallb-system
```

Once the metallb controller restarts it'll begin to reip the external service IP associations which typically
requires DNS entry updates. This change including the DNS refresh (TTL) time will be disruptive.

> [!TIP]
> **Node Exclusion from LoadBalancer**
>
>
> To exclude specific nodes from receiving loadbalancer traffic, you can add the following
> label to the nodes you want to exclude.
>
> ``` shell
> kubectl label node <node-name> node.kubernetes.io/exclude-from-external-load-balancers=true
> ```
>
> Replace `<node-name>` with the name of the node you want to exclude. This will prevent MetalLB
> from assigning load balancer IPs to services on that node.
>
> Conversely, to include a node back into loadbalancer assignments, you can remove the label.
>
> ``` shell
> kubectl label node <node-name> node.kubernetes.io/exclude-from-external-load-balancers-
> ```
>
> For more information on this well known label, refer to the
> [Kubernetes documentation](https://kubernetes.io/docs/reference/labels-annotations-taints/#node-kubernetes-io-exclude-from-external-load-balancers).

