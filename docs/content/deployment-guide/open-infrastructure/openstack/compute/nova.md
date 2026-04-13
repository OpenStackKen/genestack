---
title: "Nova"
description: "Virtualization Infrastructure as a Service (IaaS) in OpenStack"
weight: 40
---

[Nova](https://docs.openstack.org/nova/latest/) is the compute service within the OpenStack ecosystem, responsible for provisioning, scheduling, and managing virtual machine instances. This document covers the deployment of OpenStack Nova using Genestack.

Run the Nova deployment Script `/opt/genestack/bin/install-nova.sh`

```bash {include="bin/install-nova.sh"}
```

> [!TIP]
>
> You may need to provide custom values to configure your openstack services, for a simple single region or lab deployment you can supply an additional overrides flag using the example found at `base-helm-configs/aio-example-openstack-overrides.yaml`.
> In other cases such as a multi-region deployment you may want to view the [Multi-Region Support](/operations-guide/multi-region-support/) guide to for a workflow solution.

> [!NOTE]
>
> The above command is setting the ceph as disabled. While the K8S infrastructure has Ceph, we're not exposing ceph to our openstack environment.

If running in an environment that doesn't have hardware virtualization extensions add the following two `set` switches to the install command.

``` shell
--set conf.nova.libvirt.virt_type=qemu --set conf.nova.libvirt.cpu_mode=none
```

> [!TIP]
>
> You may need to provide custom values to configure your openstack services, for a simple single region or lab deployment you can supply an additional overrides flag using the example found at `base-helm-configs/aio-example-openstack-overrides.yaml`.
> In other cases such as a multi-region deployment you may want to view the [Multi-Region Support](/operations-guide/multi-region-support/) guide to for a workflow solution.
