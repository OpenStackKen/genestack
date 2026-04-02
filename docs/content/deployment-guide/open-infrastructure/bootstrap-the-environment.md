---
title: "Bootstrap the Environment"
weight: 5
---
The basic setup requires ansible, ansible collection and helm installed to
install Kubernetes and OpenStack Helm:

``` shell
/opt/genestack/bootstrap.sh
```

> [!TIP]
>
> If running this command with `sudo`, be sure to run with `-E`.
> `sudo -E /opt/genestack/bootstrap.sh`. This will ensure your active
> environment is passed into the bootstrap command.
>

Once the bootstrap is completed the default Kubernetes provider will be
configured inside `/etc/genestack/provider` and currently defaults to
kubespray.

The ansible inventory is expected at `/etc/genestack/inventory`.
