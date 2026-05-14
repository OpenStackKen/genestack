---
title: "Getting the Code"
weight: 20
---
Before you can do anything we need to get the code. Because we've sold our soul to the submodule devil, you're going to need to recursively clone the repo into your location.

> [!GENESTACK]
>
> Throughout the all our documentation and examples the genestack code base will be assumed to be in `/opt`.

``` shell
git clone --recurse-submodules -j4 https://github.com/rackerlabs/genestack /opt/genestack
```

Once the repository is present under `/opt/genestack`, you can proceed in two ways:

- [Hyperconverged Lab](/deployment-guide/hyperconverged-lab/) → Create an all-in-one Genestack cloud for learning, testing, and and proof-of-concept environments.

- [Open Infrastructure](/deployment-guide/open-infrastructure/) → Deploy a production-style Genestack cloud.
