---
title: "Placement"
description: "VM scheduling and placement in OpenStack"
weight: 30
---

> [!genestack]
>
> To deploy Placement, run the Placement deployment script `/opt/genestack/bin/install-placement.sh`.

```bash {include="bin/install-placement.sh"}
```

> [!TIP]
>
> You may need to provide custom values to configure your OpenStack services.
> For a simple single-region or lab deployment, you can supply an additional
> overrides flag using the example found at
> `base-helm-configs/aio-example-openstack-overrides.yaml`. For multi-region
> environments, review the
> [Multi-Region Support](/operations-guide/genestack/multi-region/) workflow.
