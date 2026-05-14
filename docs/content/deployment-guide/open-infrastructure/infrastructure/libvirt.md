---
title: "Libvirt"
weight: 120
---

The first part of the compute kit is Libvirt.

## Run the package deployment

> [!EXAMPLE]
>
> Run the libvirt deployment script.

```bash {include="bin/install-libvirt.sh"}
```

Once deployed, you can validate functionality on your compute hosts with `virsh`.

```bash
kubectl exec -it $(kubectl get pods -l application=libvirt -o=jsonpath='{.items[0].metadata.name}' -n openstack) -n openstack -- virsh list
```
