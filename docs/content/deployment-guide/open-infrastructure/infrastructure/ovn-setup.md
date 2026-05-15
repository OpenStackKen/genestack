---
title: "OVN"
weight: 130
---
Deploy Open vSwitch [OVN](https://www.ovn.org/en/).

> [!NOTE]
>
> Genestack does not deploy Open vSwitch itself, but it does assume OVN is
> present. In the standard Kubespray-based environment, OVN is already deployed
> as the Kubernetes networking solution. OpenStack then integrates with that
> existing OVN control plane and follows the same scaling, maintenance, and
> lifecycle practices as Kube-OVN.

## Configure OVN for OpenStack

After deployment, Neutron must be configured to work with the integrated OVN
environment. That is done through node annotations. The examples below label
all matching nodes the same way, but the model is flexible: different nodes can
carry different bridge, port, VLAN, bond, gateway, and availability-zone
layouts.

## OVN Annotations

| <div style="width:220px">key</div> | type | <div style="width:128px">value</div> | notes |
|:-----|--|:----------------:|:------|
| **ovn.openstack.org/int_bridge** | str | `br-int` | The name of the integration bridge that will be used. |
| **ovn.openstack.org/bridges** | str | `br-ex` | Comma-separated list of bridges that will be created and plugged into OVS on a given node. |
| **ovn.openstack.org/ports** | str | `br-ex:bond1` | Comma-separated list of bridge mappings. Maps values from **bridges** to physical devices or bonds on a given node. |
| **ovn.openstack.org/bonds** | str | `br-ex:bond0:eno1+eno3:balance-tcp:active` | Comma-separated list of bond definitions. Format: `bridge:bondname:member1+member2:mode:lacp`. |
| **ovn.openstack.org/bond-options** | str | `bond0:mii-monitor-interval=100,lacp-time=fast` | Comma-separated list of additional bond options. Format: `bondname:option1=value1,option2=value2`. |
| **ovn.openstack.org/vlans** | str | `bond0.126:bond0:126:1500` | Comma-separated list of host VLAN interfaces to create before attaching ports. Format: `interface_name:parent_interface:vlan_id:mtu`. |
| **ovn.openstack.org/mappings** | str | `physnet1:br-ex` | Comma-separated list of Neutron mappings. Maps provider network names to a bridge defined by **ports** or **bonds**. |
| **ovn.openstack.org/availability_zones** | str | `az1` | Colon-separated list of availability zones a given node will serve. |
| **ovn.openstack.org/gateway** | str | `enabled` | If set to `enabled`, the node is marked as a gateway. |

### Gather the Network-Enabled Nodes

Set the annotations needed within the environment to meet the needs of your
workloads and hardware layout.

> [!TIP]
>
> For post-deployment administration, troubleshooting, and operational
> workflows, review the
> [OVN operations guide](/operations-guide/infrastructure/ovn/kube-ovn/).

### Set `ovn.openstack.org/int_bridge`

Set the name of the OVS integration bridge. In most environments this should
be `br-int`. While Genestack expects this implicitly, defining it explicitly on
the node removes ambiguity.

```bash
kubectl annotate \
        nodes \
        -l openstack-compute-node=enabled -l openstack-network-node=enabled \
        ovn.openstack.org/int_bridge='br-int'
```

### Set `ovn.openstack.org/bridges`

Set the name of the OVS bridges we'll use. These are the bridges you will use on your hosts within OVS. The option is a string and comma separated. You can define as many OVS type bridges you need or want for your environment.

> [!NOTE]
>
> The functional example here annotates all nodes; however, not all nodes have to have the same setup.

```bash
kubectl annotate \
        nodes \
        -l openstack-compute-node=enabled -l openstack-network-node=enabled \
        ovn.openstack.org/bridges='br-ex'
```

### Set `ovn.openstack.org/ports`

Set the port mapping for OVS interfaces to a local physical interface on a given machine. This option uses a colon between the OVS bridge and the physical interface, `OVS_BRIDGE:PHYSICAL_INTERFACE_NAME`. Multiple bridge mappings can be defined by separating values with a comma.

> [!NOTE]
>
> If using bonds, the port mapping should reference the bond name (e.g., `br-ex:bond0`) instead of individual physical interfaces. See the bonds section below for configuring bonded interfaces.

```bash
kubectl annotate \
        nodes \
        -l openstack-compute-node=enabled -l openstack-network-node=enabled \
        ovn.openstack.org/ports='br-ex:bond1'
```

### Set `ovn.openstack.org/bonds` (Optional)

Configure OVS bonds for link aggregation and redundancy. This annotation creates bonded interfaces using multiple physical network interfaces.

**Format:** `bridge:bondname:member1+member2+member3:mode:lacp`

**Parameters:**
- `bridge`: The OVS bridge to attach the bond to (e.g., `br-ex`)
- `bondname`: Name of the bond interface (e.g., `bond0`)
- `members`: Physical interfaces to include in the bond, separated by `+` (e.g., `eno1+eno3`)
- `mode`: Bond mode - `balance-slb` (source MAC) or `balance-tcp` (TCP/UDP ports for LACP)
- `lacp`: LACP mode - `off`, `active`, or `passive`

**Example: LACP Bond**
```bash
### Set `ovn.openstack.org/vlans` (Optional)

Create Linux VLAN subinterfaces on the host before OVN attaches them to an OVS
bridge. This is useful when the host must keep the parent interface while OVN
consumes a tagged child interface such as `bond0.126`.

Format: `interface_name:parent_interface:vlan_id:mtu`

Parameters:
- `interface_name`: name of the VLAN interface to create, for example `bond0.126`
- `parent_interface`: existing host interface that carries the VLAN, for example `bond0`
- `vlan_id`: numeric VLAN tag
- `mtu`: MTU to apply to the VLAN interface

Example: external uplink on VLAN 126

```bash
kubectl annotate \
        nodes \
        -l openstack-network-node=enabled \
        ovn.openstack.org/vlans='bond0.126:bond0:126:1500'

kubectl annotate \
        nodes \
        -l openstack-network-node=enabled \
        ovn.openstack.org/ports='br-ex:bond0.126'
```

> [!NOTE]
>
> `ovn.openstack.org/vlans` only creates the host VLAN device. You must still
> reference that VLAN interface through `ovn.openstack.org/ports` so it is
> attached to the correct bridge.

### Set `ovn.openstack.org/bonds` (Optional)

Configure OVS bonds for link aggregation and redundancy.

Format: `bridge:bondname:member1+member2+member3:mode:lacp`

Parameters:
- `bridge`: the OVS bridge to attach the bond to, for example `br-ex`
- `bondname`: name of the bond interface, for example `bond0`
- `members`: physical interfaces to include in the bond, separated by `+`
- `mode`: `balance-slb` or `balance-tcp`
- `lacp`: `off`, `active`, or `passive`

Example: LACP bond

```bash
kubectl annotate \
        nodes \
        -l openstack-network-node=enabled \
        ovn.openstack.org/bonds='br-ex:bond0:eno1+eno3:balance-tcp:active'
```

**Example: Multiple Bonds**
```bash
kubectl annotate \
        nodes \
        node1 \
        ovn.openstack.org/bonds='br-ex:bond0:eno1+eno3:balance-tcp:active,br-provider:bond1:eno5+eno7:balance-slb:off'
```

### Set `ovn.openstack.org/bond-options` (Optional)

Configure additional bond options for fine-tuning bond behavior. This annotation is used in conjunction with `ovn.openstack.org/bonds`.

**Format:** `bondname:option1=value1,option2=value2`

**Supported Options:**
- `mii-monitor-interval`: MII link monitoring interval in milliseconds (e.g., `100`)
- `bond-detect-mode`: Link detection method - `miimon` or `carrier`
- `lacp-time`: LACP heartbeat rate - `fast` (1 second) or `slow` (30 seconds)
- `lacp-fallback-ab`: Enable fallback to active-backup if LACP fails - `true` or `false`
- `updelay`: Delay in milliseconds before enabling a link after it comes up
- `downdelay`: Delay in milliseconds before disabling a link after it goes down
- `rebalance-interval`: Rebalancing interval in milliseconds (for `balance-slb` mode)

**Example: LACP with MII Monitoring**

```bash
kubectl annotate \
        nodes \
        -l openstack-network-node=enabled \
        ovn.openstack.org/bond-options='bond0:mii-monitor-interval=100,lacp-time=fast,bond-detect-mode=miimon'
```

**Example: Multiple Bonds with Different Options**
```bash
kubectl annotate \
        nodes \
        node1 \
        ovn.openstack.org/bond-options='bond0:mii-monitor-interval=100,lacp-time=fast,bond1:updelay=500,downdelay=500'
```

> [!TIP]
>
> **OVS Bond Modes**
>
> - **balance-slb**: Source Load Balancing - distributes traffic based on source MAC address. Does not require LACP support on the switch.
> - **balance-tcp**: Balances based on L3/L4 headers (IP addresses and TCP/UDP ports). Requires LACP (`lacp=active` or `lacp=passive`).
>
> For 802.3ad LACP bonding, use `mode=balance-tcp` with `lacp=active`.

### Set `ovn.openstack.org/mappings`

Set the Neutron bridge mapping. This maps the Neutron interfaces to the ovs bridge names. These are colon delimitated between `NEUTRON_INTERFACE:OVS_BRIDGE`. Multiple bridge mappings can be defined here and are separated by commas.

> [!note]
>
> Neutron interfaces are string value and can be anything you want. The `NEUTRON_INTERFACE` value defined will be used when you create provider type networks after the cloud is online.

```bash
kubectl annotate \
        nodes \
        -l openstack-compute-node=enabled -l openstack-network-node=enabled \
        ovn.openstack.org/mappings='physnet1:br-ex'
```

### Set `ovn.openstack.org/availability_zones`

Set the OVN availability zones, which in turn create Neutron availability zones. Multiple values can be defined as a colon-separated string, for example `nova:az1:az2:az3`.

```bash
kubectl annotate \
        nodes \
        -l openstack-compute-node=enabled -l openstack-network-node=enabled \
        ovn.openstack.org/availability_zones='az1'
```

> [!NOTE]
>
> Any availability zone defined here should also be defined within your `neutron.conf`. The "az1" availability zone is assumed by Genestack; however, because we're running in a mixed OVN environment, we define where we're allowed to execute OpenStack workloads ensuring we're not running workloads in an environment that doesn't have the network resources to support it.
>
> Additionally, an availability zone can be used on different nodes and used to define where gateways reside. If you have multiple availability zones, you will need to define where the gateways will reside within your environment.

### Set `ovn.openstack.org/gateway`

Define where the gateways nodes will reside. There are many ways to run this, some like every compute node to be a gateway, some like dedicated gateway hardware. Either way you will need at least one gateway node within your environment.
NOTE: In the following example, we will apply the 'ovn.openstack.org/gateway' to dedicated network nodes.  You will want to change the node filter to the specific nodes you wish to use as ovn gateway nodes.

```bash
kubectl annotate \
        nodes \
        $(kubectl get nodes | awk '/network/ {print $1}') \
        ovn.openstack.org/gateway='enabled'
```

## Run the OVN integration

With all of the annotations defined, we can now apply the network policy with the following command.

```bash
kubectl apply -k /etc/genestack/kustomize/ovn/base
```

After running the setup, nodes will have the label `ovn.openstack.org/configured` with a date stamp when it was configured. If there's ever a need to reconfigure a node, simply remove the label and the DaemonSet will take care of it automatically.

### Reconfiguring Nodes

The OVN setup includes intelligent state management that safely handles configuration changes:

**State Tracking:**
- Previous configuration is stored in per-node ConfigMaps named `ovn-state-<nodename>`
- The setup script compares previous state with new annotations
- Changes are applied incrementally to prevent network disruption

**Safe Port Migration:**
When changing port assignments (e.g., moving from `eno1` to `eno3`), the setup will:
1. Remove the old port (`eno1`) from the bridge
2. Add the new port (`eno3`) to the bridge
3. Update the state ConfigMap

This prevents network loops that could occur if both ports were simultaneously connected to the bridge.

**To reconfigure a node:**

1. Update the node annotations with new configuration
2. Remove the configured label:
   ```bash
   kubectl label node <node-name> ovn.openstack.org/configured-
   ```
3. The DaemonSet will detect the unlabeled node and reapply configuration
4. Old ports/bonds will be cleaned up, new configuration applied

**Example: Changing from single interface to bonded interfaces**

```bash
# Update annotations
kubectl annotate nodes node1 --overwrite \
    ovn.openstack.org/ports='br-ex:bond0' \
    ovn.openstack.org/bonds='br-ex:bond0:eno1+eno3:balance-tcp:active' \
    ovn.openstack.org/bond-options='bond0:mii-monitor-interval=100,lacp-time=fast'

# Trigger reconfiguration
kubectl label node node1 ovn.openstack.org/configured-
```

The setup will remove any existing single interface ports and create the bond configuration.

> [!tip]
>
> **Setup your OVN backup**
>
> To upload backups to Swift with tempauth, edit `/etc/genestack/kustomize/ovn-backup/base/ovn-backup.config` to set `SWIFT_TEMPAUTH_UPLOAD' "true"`, edit the other related options appropriately (i.e., set the CONTAINER) and fill the `ST_AUTH`, `ST_USER`, and `ST_KEY` as appropriate for the Swift CLI client in the `swift-tempauth.env` file and then run:

```bash
kubectl apply -k /etc/genestack/kustomize/ovn-backup/base \
--prune -l app=ovn-backup \
--prune-allowlist=core/v1/Secret \
--prune-allowlist=core/v1/ConfigMap
```

> [!tip]
>
> If you need to change variables in the future, you can edit the relevant files and use `kubectl` with these prune options to avoid accumulating old ConfigMaps and Secrets from successive `kubectl apply` operations, but you can omit the pruning options if desired.

### Centralize `kube-ovn-controller` pods

By default, _Kubespray_ deploys _Kube-OVN_ allowing [`kube-ovn-controller` pods](https://kubeovn.github.io/docs/stable/en/reference/architecture/#kube-ovn-controller), which play a central role, to distribute across various kinds of cluster nodes.  In _Genestack_, this would include compute nodes and other kinds of nodes. By contrast, `ovn-central` pods, which also play a crucial central role, run only on nodes labelled `"kube-ovn/role": "master"`. A _Genestack_ installation will typically have control functions centralized on a small set of nodes, which you may have different resource allocations and different redundancy and uptime requirements for relative to other types of nodes, so you can set the `kube-ovn-controller` pods to run in the same location as [`ovn-central`](https://kubeovn.github.io/docs/stable/en/reference/architecture/#ovn-central) on _Kube-OVN_ master nodes (which most likely simply match your k8s cluster control nodes unless you've customized it):

```bash
kubectl -n kube-system patch deployment kube-ovn-controller -p '{
  "spec": {
    "template": {
      "spec": {
        "nodeSelector": {
          "kube-ovn/role": "master",
          "kubernetes.io/os": "linux"
        }
      }
    }
  }
}
'
```

This helps keep critical control functions on a known set of nodes.
