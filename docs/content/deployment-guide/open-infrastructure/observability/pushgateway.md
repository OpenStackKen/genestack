---
title: "Pushgateway"
description: "Promethus Pushgateway"
weightL: 30
---

Prometheus Pushgateway is useful for short-lived jobs, such as Kubernetes `CronJob` workloads, that need to push metrics before they exit.

## Paths

- Base Helm values: `/opt/genestack/base-helm-configs/prometheus-pushgateway/`
- Service overrides: `/etc/genestack/helm-configs/prometheus-pushgateway/`
- Kustomize overlay: `/etc/genestack/kustomize/prometheus-pushgateway/overlay/`

## Install

```bash
/opt/genestack/bin/install-prometheus-pushgateway.sh
```

## Verify

```bash
kubectl -n monitoring get pods -l app.kubernetes.io/instance=prometheus-pushgateway
kubectl -n monitoring get servicemonitor prometheus-pushgateway
```
