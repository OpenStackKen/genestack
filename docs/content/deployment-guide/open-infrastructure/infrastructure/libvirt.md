---
title: "Libvirt"
weight: 120
---
The first part of the compute kit is [libvirt](https://libvirt.org/).

## Run the package deployment

Run the libvirt deployment Script `/opt/genestack/bin/install-libvirt.sh`

```bash {include="bin/install-libvirt.sh"}
```
```

```

Once deployed you can validate functionality on your compute hosts with `virsh`

``` shell
kubectl exec -it $(kubectl get pods -l application=libvirt -o=jsonpath='{.items[0].metadata.name}' -n openstack) -n openstack -- virsh list
```
