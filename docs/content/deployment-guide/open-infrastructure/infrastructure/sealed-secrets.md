---
title: "Sealed Secrets"
weight: 170
---
Installing [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets):

Run the deployment Script `/opt/genestack/bin/install-sealed-secrets.sh`

```bash {include="bin/install-sealed-secrets.sh"}
```
## Verify readiness with the following command.

``` shell
kubectl --namespace sealed-secrets get horizontalpodautoscaler.autoscaling sealed-secrets -w
```
