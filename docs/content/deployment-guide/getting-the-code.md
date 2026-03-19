---
title: "Getting the Code"
weight: 20
---
Before you can do anything we need to get the code. Because we've sold our soul to the submodule devil, you're going to need to recursively clone the repo into your location.

> [!NOTE]
>
>
> Throughout the all our documentation and examples the genestack code base will be assumed to be in `/opt`.
>

``` shell
git clone --recurse-submodules -j4 https://github.com/rackerlabs/genestack /opt/genestack
```

Once the repository is present under `/opt/genestack`, you can proceed in two ways:

- Create an all-in-one Genestack cloud for test and proof-of-concept environments by building a [Hyperconverged Lab](/deployment-guide/hyperconverged-lab/)

- Deploy a productunction-style Genestack cloud by deploying [Open Infrastructure](/deployment-guide/open-infrastructure/).
