---
title: "Placement"
description: "VM scheduling and placement in OpenStack"
weight: 30
---

[Placement](https://docs.openstack.org/placement/latest/) is the resource inventory and allocation service within the OpenStack ecosystem, tracking available compute-related resources and helping schedulers make accurate placement decisions. This document covers the deployment of OpenStack Placement using Genestack.

Run the Placement deployment Script `/opt/genestack/bin/install-placement.sh`

```bash {include="bin/install-placement.sh"}
```
```

```

> [!TIP]
>
> You may need to provide custom values to configure your openstack services, for a simple single region or lab deployment you can supply an additional overrides flag using the example found at `base-helm-configs/aio-example-openstack-overrides.yaml`.
> In other cases such as a multi-region deployment you may want to view the [Multi-Region Support](/operations-guide/multi-region-support/) guide to for a workflow solution.
