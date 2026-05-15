---
title: "MetalLB"
weight: 40
---

The MetalLb loadbalancer can be setup by editing the following file `metallb-openstack-service-lb.yml`, You will need to add your "external" VIP(s) to the loadbalancer so that they can be used within services. These IP addresses are unique and will need to be customized to meet the needs of your environment.

> [!tip]
>
> When L2Advertisement is used, you should use a CIDR that is not overlapping with any local interface CIDR.
> This also enables later migration to BGP advertisement.

## Create the MetalLB namespace

``` shell
kubectl apply -f /etc/genestack/manifests/metallb/metallb-namespace.yaml
```

## Install MetalLB

> [!genestack]
>
> Run the MetalLB deployment Script `/opt/genestack/bin/install-metallb.sh`

You can include paramaters to deploy aio or base-monitoring. No paramaters deploys base

```bash {include="bin/install-metallb.sh"}
```

## Example LB manifest

> [!example]
>
> Example for `metallb-openstack-service-lb.yml` file.

```yaml {include="manifests/metallb/metallb-openstack-service-lb.yml"}
```

> [!tip]
>
> Edit the `/etc/genestack/manifests/metallb/metallb-openstack-service-lb.yml` file following the comment instructions with the details of your cluster.

The file `metallb-openstack-service-lb.yml` is initially provided during bootstrap for genestack.

Verify the deployment of MetalLB by checking the pods in the `metallb-system` namespace.

```bash
kubectl --namespace metallb-system get deployment.apps/metallb-controller
```

Once MetalLB is operational, apply the metallb service manifest.

```bash
kubectl apply -f /etc/genestack/manifests/metallb/metallb-openstack-service-lb.yml
```

## Re-IP the advertisement pools

In situations where the advertisement pools must be changed, the following disruptive procedure can be used:

Update existing metallb configuration:

```bash
kubectl -n metallb-system delete IPAddressPool/primary
kubectl -n metallb-system delete IPAddressPool/gateway-api-external
kubectl apply -f /etc/genestack/manifests/metallb/metallb-openstack-service-lb.yml
```

Restart the metallb controller:

```bash
kubectl rollout restart deployment metallb-controller -n metallb-system
```

Once the metallb controller restarts it'll begin to reip the external service IP associations which typically
requires DNS entry updates. This change including the DNS refresh (TTL) time will be disruptive.

> [!TIP]
>
> **Node Exclusion from LoadBalancer**
>
> To exclude specific nodes from receiving loadbalancer traffic, you can add the following
> label to the nodes you want to exclude.

```bash
kubectl label node <node-name> node.kubernetes.io/exclude-from-external-load-balancers=true
```
Replace `<node-name>` with the name of the node you want to exclude. This will prevent MetalLB from assigning load balancer IPs to services on that node.

Conversely, to include a node back into loadbalancer assignments, you can remove the label.

```bash
kubectl label node <node-name> node.kubernetes.io/exclude-from-external-load-balancers-
```

For more information on this well known label, refer to the [Kubernetes documentation](https://kubernetes.io/docs/reference/labels-annotations-taints/#node-kubernetes-io-exclude-from-external-load-balancers).
