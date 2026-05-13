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

```shell
kubectl annotate \
        nodes \
        -l openstack-compute-node=enabled -l openstack-network-node=enabled \
        ovn.openstack.org/int_bridge='br-int'
```

### Set `ovn.openstack.org/bridges`

Set the names of the OVS bridges to create on the host. Multiple bridge names
can be defined as a comma-separated string.

> [!NOTE]
>
> The example below annotates all matching nodes, but not every node must have
> the same bridge layout.

```shell
kubectl annotate \
        nodes \
        -l openstack-compute-node=enabled -l openstack-network-node=enabled \
        ovn.openstack.org/bridges='br-ex'
```

### Set `ovn.openstack.org/ports`

Set the mapping between an OVS bridge and a local host interface.

Format: `OVS_BRIDGE:PHYSICAL_INTERFACE_NAME`

Multiple mappings can be defined by separating values with commas.

> [!NOTE]
>
> If you are using bonds, the port mapping should reference the bond name, such
> as `br-ex:bond0`, instead of the individual physical interfaces.

```shell
kubectl annotate \
        nodes \
        -l openstack-compute-node=enabled -l openstack-network-node=enabled \
        ovn.openstack.org/ports='br-ex:bond1'
```

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

```shell
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

```shell
kubectl annotate \
        nodes \
        -l openstack-network-node=enabled \
        ovn.openstack.org/bonds='br-ex:bond0:eno1+eno3:balance-tcp:active'
```

Example: multiple bonds

```shell
kubectl annotate \
        nodes \
        node1 \
        ovn.openstack.org/bonds='br-ex:bond0:eno1+eno3:balance-tcp:active,br-provider:bond1:eno5+eno7:balance-slb:off'
```

### Set `ovn.openstack.org/bond-options` (Optional)

Configure additional bond options for fine-tuning bond behavior. This is used
in conjunction with `ovn.openstack.org/bonds`.

Format: `bondname:option1=value1,option2=value2`

Supported options:
- `mii-monitor-interval`
- `bond-detect-mode`
- `lacp-time`
- `lacp-fallback-ab`
- `updelay`
- `downdelay`
- `rebalance-interval`

Example: LACP with MII monitoring

```shell
kubectl annotate \
        nodes \
        -l openstack-network-node=enabled \
        ovn.openstack.org/bond-options='bond0:mii-monitor-interval=100,lacp-time=fast,bond-detect-mode=miimon'
```

Example: multiple bonds with different options

```shell
kubectl annotate \
        nodes \
        node1 \
        ovn.openstack.org/bond-options='bond0:mii-monitor-interval=100,lacp-time=fast,bond1:updelay=500,downdelay=500'
```

> [!TIP]
>
> `balance-slb` uses source load balancing and does not require LACP support on
> the upstream switch. `balance-tcp` balances using L3 and L4 headers and is
> the normal choice for 802.3ad/LACP deployments.

### Set `ovn.openstack.org/mappings`

Set the Neutron bridge mapping. This maps Neutron provider network names to the
OVS bridge names used on the host.

Format: `NEUTRON_INTERFACE:OVS_BRIDGE`

Multiple mappings can be defined and separated by commas.

> [!NOTE]
>
> `NEUTRON_INTERFACE` is an arbitrary string value. The exact value defined
> here is what you will later reference when creating provider networks.

```shell
kubectl annotate \
        nodes \
        -l openstack-compute-node=enabled -l openstack-network-node=enabled \
        ovn.openstack.org/mappings='physnet1:br-ex'
```

### Set `ovn.openstack.org/availability_zones`

Set the OVN availability zones, which in turn create Neutron availability
zones. Multiple values can be defined as a colon-separated string, for example
`nova:az1:az2:az3`.

```shell
kubectl annotate \
        nodes \
        -l openstack-compute-node=enabled -l openstack-network-node=enabled \
        ovn.openstack.org/availability_zones='az1'
```

> [!NOTE]
>
> Any availability zone defined here should also be defined within
> `neutron.conf`. The `az1` availability zone is assumed by Genestack, but in a
> mixed OVN environment you should explicitly define where OpenStack workloads
> may be scheduled. Availability zones can also be used to control where
> gateways reside.

### Set `ovn.openstack.org/gateway`

Define which nodes will operate as gateway nodes. Some environments prefer
every compute node to be a gateway; others use dedicated gateway hardware.
Either way, at least one gateway node is required.

> [!NOTE]
>
> The example below targets dedicated network nodes. Adjust the node selector
> to match the gateway nodes in your environment.

```shell
kubectl annotate \
        nodes \
        $(kubectl get nodes | awk '/network/ {print $1}') \
        ovn.openstack.org/gateway='enabled'
```

## Run the OVN Integration

With the annotations defined, apply the OVN integration policy:

```shell
kubectl apply -k /etc/genestack/kustomize/ovn/base
```

After setup runs, nodes receive the label `ovn.openstack.org/configured` with a
date stamp. To reconfigure a node, remove the label and let the DaemonSet
reconcile it again.

### Reconfiguring Nodes

The OVN setup includes basic state management that safely handles
configuration changes:

- Previous configuration is stored in per-node ConfigMaps named `ovn-state-<nodename>`
- The setup compares prior state with new annotations
- Changes are applied incrementally to avoid unnecessary disruption

When changing port assignments, the setup removes the old port before adding
the new port and updates the node state accordingly. This prevents transient
bridge loops caused by both ports being attached at once.
