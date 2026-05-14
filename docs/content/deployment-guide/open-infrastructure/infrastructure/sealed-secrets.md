---
title: "Sealed Secrets"
weight: 170
---
## Install Sealed Secrets

Run the deployment script `/opt/genestack/bin/install-sealed-secrets.sh`.

```bash {include="bin/install-sealed-secrets.sh"}
```
## Verify readiness with the following command.

```shell
kubectl --namespace sealed-secrets get horizontalpodautoscaler.autoscaling sealed-secrets -w
```
