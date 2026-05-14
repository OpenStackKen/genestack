---
title: "Nova"
description: "Virtualization Infrastructure as a Service (IaaS) in OpenStack"
weight: 40
---

> [!genestack]
>
> Run the Nova deployment script `/opt/genestack/bin/install-nova.sh`.

```bash {include="bin/install-nova.sh"}
```

> [!tip]
>
>
> You may need to provide custom values to configure your openstack services, for a simple single region or lab deployment you can supply an additional overrides flag using the example found at `base-helm-configs/aio-example-openstack-overrides.yaml`.
> In other cases such as a multi-region deployment you may want to view the [Multi-Region Support](/operations-guide/genestack/multi-region/) guide to for a workflow solution.
>

> [!note]
>
>
> The above command is setting the ceph as disabled. While the K8S infrastructure has Ceph, we're not exposing ceph to our openstack environment.
>

If running in an environment that doesn't have hardware virtualization extensions add the following two `set` switches to the install command.

```bash
--set conf.nova.libvirt.virt_type=qemu --set conf.nova.libvirt.cpu_mode=none
```

> [!TIP]
>
>
> You may need to provide custom values to configure your openstack services, for a simple single region or lab deployment you can supply an additional overrides flag using the example found at `base-helm-configs/aio-example-openstack-overrides.yaml`.
> In other cases such as a multi-region deployment you may want to view the [Multi-Region Support](/operations-guide/genestack/multi-region/) guide to for a workflow solution.
