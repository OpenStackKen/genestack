---
title: "Install Kube OVN"
weight: 250
---
The Kube-OVN project is a Kubernetes Network Plugin that uses OVN as the network provider. It
is a CNI plugin that provides a network solution for Kubernetes. It is a lightweight, scalable,
and easy-to-use network solution for Kubernetes.

## Prerequisites

The override values file for Kube-OVN can be found in `/etc/genestack/helm-configs/kube-ovn/kube-ovn-helm-overrides.yaml`
and should be setup-up before running the deployment. In a common production ready setup, the only values that will
likely need to be defined is the network interface that will Kube-OVN will bind to.

> [!IMPORTANT]
> **Example Kube-OVN Helm Overrides**
>
>
> In the example below, the `IFACE` and `VLAN_INTERFACE_NAME` are the only values that need to be defined and
> are set to `br-overlay`. If you intend to enable hardware offloading, you will need to set the `IFACE` to the
> a physical interface that supports hardware offloading.
>

### Default

``` yaml
networking:
  IFACE: "br-overlay"
  vlan:
    VLAN_INTERFACE_NAME: "br-overlay"
```


### Talos

``` yaml
global:                          # This is needed to
  registry:                      # Allow for pulling
    address: docker.io/kubeovn   # Kube-OVN version 1.14.10
    imagePullSecrets: []
networking:
  IFACE: eno1
  vlan:
    VLAN_INTERFACE_NAME: eno1
OPENVSWITCH_DIR: /var/lib/openvswitch
OVN_DIR: /var/lib/ovn
DISABLE_MODULES_MANAGEMENT: true
```


For a full review of all the available options, see the Kube-OVN base helm overrides file.

> [!IMPORTANT]
> **Example Kube-OVN Helm Overrides**
>
>
> ``` yaml
> # Default values for kubeovn.
> # This is a YAML-formatted file.
> # Declare variables to be passed into your templates.
> ---
> global:
>   registry:
>     address: ghcr.io/rackerlabs/genestack-images
>     imagePullSecrets: []
>   images:
>     kubeovn:
>       repository: kube-ovn
>       vpcRepository: vpc-nat-gateway
>       tag: v1.15.4
>       support_arm: true
>       thirdparty: true
> 
> image:
>   pullPolicy: IfNotPresent
> 
> replicaCount: 3
> 
> namespace: kube-system
> 
> MASTER_NODES: ""
> MASTER_NODES_LABEL: "kube-ovn/role=master"
> 
> networking:
>   # NET_STACK defaults to ipv4
>   NET_STACK: ipv4
>   ENABLE_SSL: true
>   # network type could be geneve or vlan
>   NETWORK_TYPE: geneve
>   # tunnel type could be geneve, vxlan or stt
>   TUNNEL_TYPE: geneve
>   IFACE: "br-overlay"
>   DPDK_TUNNEL_IFACE: "br-phy"
>   EXCLUDE_IPS: ""
>   POD_NIC_TYPE: "veth-pair"
>   vlan:
>     PROVIDER_NAME: "provider"
>     VLAN_INTERFACE_NAME: "br-overlay"
>     # VLAN_NAME: "ovn-vlan"
>     # VLAN_ID: "100"
>   EXCHANGE_LINK_NAME: false
>   ENABLE_EIP_SNAT: false
>   DEFAULT_SUBNET: "ovn-default"
>   DEFAULT_VPC: "ovn-cluster"
>   NODE_SUBNET: "join" # mesh network
>   ENABLE_ECMP: true
>   ENABLE_METRICS: true
>   # comma-separated string of nodelocal DNS ip addresses
>   NODE_LOCAL_DNS_IP: ""
>   PROBE_INTERVAL: 60000
>   OVN_NORTHD_PROBE_INTERVAL: 15000
>   OVN_LEADER_PROBE_INTERVAL: 15
>   OVN_REMOTE_PROBE_INTERVAL: 30000
>   OVN_REMOTE_OPENFLOW_INTERVAL: 180
>   OVN_NORTHD_N_THREADS: 4  # Number of threads for ovn-northd, default is 4 production environments could set it to a higher value.
>   ENABLE_COMPACT: true
> 
> func:
>   ENABLE_LB: true
>   ENABLE_NP: true
>   ENABLE_EXTERNAL_VPC: true
>   HW_OFFLOAD: false  # Enable hardware offload, if supported by the underlying network hardware.
>   ENABLE_LB_SVC: false
>   ENABLE_KEEP_VM_IP: true
>   LS_DNAT_MOD_DL_DST: true
>   LS_CT_SKIP_DST_LPORT_IPS: true
>   CHECK_GATEWAY: true
>   LOGICAL_GATEWAY: false
>   ENABLE_BIND_LOCAL_IP: true
>   SECURE_SERVING: false
>   U2O_INTERCONNECTION: false
>   ENABLE_TPROXY: false
>   ENABLE_IC: false
>   ENABLE_NAT_GW: true
>   ENABLE_OVN_IPSEC: false
>   ENABLE_ANP: false
>   SET_VXLAN_TX_OFF: false
>   OVSDB_CON_TIMEOUT: 5
>   OVSDB_INACTIVITY_TIMEOUT: 30
>   ENABLE_LIVE_MIGRATION_OPTIMIZE: true
> 
> ipv4:
>   POD_CIDR: "10.236.0.0/14"
>   POD_GATEWAY: "10.236.0.1"
>   SVC_CIDR: "10.233.0.0/18"
>   JOIN_CIDR: "100.64.0.0/16"
>   PINGER_EXTERNAL_ADDRESS: "208.67.222.222"
>   PINGER_EXTERNAL_DOMAIN: "opendns.com."
> 
> performance:
>   GC_INTERVAL: 360
>   INSPECT_INTERVAL: 300
>   OVS_VSCTL_CONCURRENCY: 150
> 
> debug:
>   ENABLE_MIRROR: false
>   MIRROR_IFACE: "mirror0"
> 
> cni_conf:
>   CNI_CONFIG_PRIORITY: "01"
>   CNI_CONF_DIR: "/etc/cni/net.d"
>   CNI_BIN_DIR: "/opt/cni/bin"
>   CNI_CONF_FILE: "/kube-ovn/01-kube-ovn.conflist"
>   LOCAL_BIN_DIR: "/usr/local/bin"
>   MOUNT_LOCAL_BIN_DIR: false
> 
> kubelet_conf:
>   KUBELET_DIR: "/var/lib/kubelet"
> 
> log_conf:
>   LOG_DIR: "/var/log"
> 
> OPENVSWITCH_DIR: "/etc/origin/openvswitch"
> OVN_DIR: "/etc/origin/ovn"
> DISABLE_MODULES_MANAGEMENT: false
> 
> nameOverride: ""
> fullnameOverride: ""
> 
> # hybrid dpdk
> HYBRID_DPDK: false
> HUGEPAGE_SIZE_TYPE: hugepages-2Mi # Default
> HUGEPAGES: 1Gi
> 
> # DPDK
> DPDK: false
> DPDK_VERSION: "19.11"
> DPDK_CPU: "1000m" # Default CPU configuration
> DPDK_MEMORY: "2Gi" # Default Memory configuration
> 
> ovn-central:
>   requests:
>     cpu: "300m"
>     memory: "200Mi"
>   limits:
>     cpu: "3"
>     memory: "4Gi"
> ovs-ovn:
>   requests:
>     cpu: "200m"
>     memory: "200Mi"
>   limits:
>     cpu: "2"
>     memory: "1000Mi"
> kube-ovn-controller:
>   requests:
>     cpu: "200m"
>     memory: "200Mi"
>   limits:
>     cpu: "1000m"
>     memory: "1Gi"
> kube-ovn-cni:
>   requests:
>     cpu: "100m"
>     memory: "100Mi"
>   limits:
>     cpu: "1000m"
>     memory: "1Gi"
> kube-ovn-pinger:
>   requests:
>     cpu: "100m"
>     memory: "100Mi"
>   limits:
>     cpu: "200m"
>     memory: "400Mi"
> kube-ovn-monitor:
>   requests:
>     cpu: "200m"
>     memory: "200Mi"
>   limits:
>     cpu: "200m"
>     memory: "200Mi"
> ```
>

### Label Kube-OVN nodes

| <div style="width:220px">key</div> | type | <div style="width:128px">value</div>  | notes |
|:-----|--|:----------------:|:------|
| **kube-ovn/role** | str | `master` | Defines where the Kube-OVN Masters will reside |
| **ovn.kubernetes.io/ovs_dp_type** | str | `kernel` | (Optional) Defines OVS DPDK mode |

> [!IMPORTANT]
> **Label all controllers as Kube-OVN control plane nodes**
>
>
> ``` shell
> kubectl label node -l beta.kubernetes.io/os=linux kubernetes.io/os=linux
> kubectl label node -l node-role.kubernetes.io/control-plane kube-ovn/role=master
> kubectl label node -l ovn.kubernetes.io/ovs_dp_type!=userspace ovn.kubernetes.io/ovs_dp_type=kernel
> ```
>

## Deployment

To run the Kube-OVN deployment, run the following command commands or script.

> [!IMPORTANT]
> **Run the Kube-OVN deployment Script `/opt/genestack/bin/install-kube-ovn.sh`**
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
> SERVICE_NAME_DEFAULT="kube-ovn"
> SERVICE_NAMESPACE="kube-system" # Note: kube-ovn uses the kube-system namespace
> 
> # Helm
> HELM_REPO_NAME_DEFAULT="kubeovn"
> HELM_REPO_URL_DEFAULT="https://kubeovn.github.io/kube-ovn"
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
> # --- Kube-OVN specific logic to determine masters and replica count ---
> MASTER_NODES=$(kubectl get nodes -l kube-ovn/role=master -o json | jq -r '[.items[].status.addresses[] | select(.type == "InternalIP") | .address] | join(",")' | sed 's/,/\\,/g')
> MASTER_NODE_COUNT=$(kubectl get nodes -l kube-ovn/role=master -o json | jq -r '.items[].status.addresses[] | select(.type=="InternalIP") | .address' | wc -l)
> 
> if [ "${MASTER_NODE_COUNT}" -eq 0 ]; then
>     echo "Error: No master nodes found labeled with 'kube-ovn/role=master'" >&2
>     echo "Be sure to label your master nodes with 'kube-ovn/role=master' before running this script." >&2
>     exit 1
> fi
> echo "Found $MASTER_NODE_COUNT master node(s) with IPs: ${MASTER_NODES//\\,/ }."
> # --------------------------------------------------------------------
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
>     --set "MASTER_NODES=${MASTER_NODES}"
>     --set "replicaCount=${MASTER_NODE_COUNT}"
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

### Deployment Verification

Once the script has completed, you can verify that the Kube-OVN pods are running by running the following command

``` shell
kubectl get subnets.kubeovn.io
```

> [!IMPORTANT]
> **Output**
>
>
> ``` shell
> NAME          PROVIDER   VPC           PROTOCOL   CIDR            PRIVATE   NAT     DEFAULT   GATEWAYTYPE   V4USED   V4AVAILABLE   V6USED   V6AVAILABLE   EXCLUDEIPS       U2OINTERCONNECTIONIP
> join          ovn        ovn-cluster   IPv4       100.64.0.0/16   false     false   false     distributed   3        65530         0        0             ["100.64.0.1"]
> ovn-default   ovn        ovn-cluster   IPv4       10.236.0.0/14   false     true    true      distributed   111      262030        0        0             ["10.236.0.1"]
> ```
>

> [!TIP]
>
>
> After the deployment, and before going into production, it is highly recommended to review the
> [Kube-OVN Backup documentation](/operational-guide/infrastructure-ovn-db-backup/), from the operators guide for setting up you backups.
>

Upon successful deployment the Kubernetes Nodes should transition into a `Ready` state. Validate the nodes are ready by
running the following command.

``` shell
kubectl get nodes
```

> [!IMPORTANT]
> **Output**
>
>
> ``` shell
> NAME                                  STATUS   ROLES                  AGE   VERSION
> compute-0.cloud.cloudnull.dev.local   Ready    control-plane,worker   24m   v1.30.4
> compute-1.cloud.cloudnull.dev.local   Ready    control-plane,worker   24m   v1.30.4
> compute-2.cloud.cloudnull.dev.local   Ready    control-plane,worker   24m   v1.30.4
> ```

