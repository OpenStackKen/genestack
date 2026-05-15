---
title: "RabbitMQ"
weight: 90
---

Deploying the RabbitMQ Operator and a RabbitMQ Cluster

## Deploy the RabbitMQ operator.

```bash
kubectl apply -k /etc/genestack/kustomize/rabbitmq-operator/base
```

> [!NOTE]
>
> The operator may take a minute to get ready, before deploying the RabbitMQ cluster, wait until the operator pod is online.

### Deploy the RabbitMQ topology operator.

```bash
kubectl apply -k /etc/genestack/kustomize/rabbitmq-topology-operator/base
```

### Deploy the RabbitMQ cluster.

```bash
kubectl apply -k /etc/genestack/kustomize/rabbitmq-cluster/overlay
```

> [!NOTE]
>
> RabbitMQ has a base configuration which is HA and production ready. If you're deploying on a small cluster the `aio` configuration may better suit the needs of the environment.

## Validate the status with the following

```bash
kubectl --namespace openstack get rabbitmqclusters.rabbitmq.com -w
```

## Epoxy upgrade notes

Genestack targets RabbitMQ `4.1.4` for the Epoxy release path. The `RabbitmqCluster` manifest pins `spec.image` explicitly to `rabbitmq:4.1.4-management` so upgrades remain predictable and do not depend on operator default image changes.

When upgrading an existing environment, re-apply the RabbitMQ cluster manifest so that the intended RabbitMQ image is reconciled.

> [!WARNING]
>
> If you rely on operator defaults rather than the pinned cluster image, your cluster may drift to an unexpected RabbitMQ server version during upgrade or reconciliation.

## RabbitMQ Operator Monitoring

RabbitMQ Operator provides ServiceMonitor and PodMonitor CRDs to expose scrape endpoints for rabbitmq
cluster and operator.

> [!WARNING]
>
> Make sure Prometheus Operator is deployed prior to running these commands. It will error out if the required CRDs are not already installed.

Check if the required CRDs are installed

```bash
kubectl get customresourcedefinitions.apiextensions.k8s.io servicemonitors.monitoring.coreos.com
```

if the CRDs are present you can run the following

```bash
kubectl apply --filename https://raw.githubusercontent.com/rabbitmq/cluster-operator/main/observability/prometheus/monitors/rabbitmq-servicemonitor.yml

kubectl apply --filename https://raw.githubusercontent.com/rabbitmq/cluster-operator/main/observability/prometheus/monitors/rabbitmq-cluster-operator-podmonitor.yml
```

then,

```bash
for file in $(curl -s https://api.github.com/repos/rabbitmq/cluster-operator/contents/observability/prometheus/rules/rabbitmq | jq -r '.[].download_url'); do   kubectl apply -n prometheus -f $file; done

for file in $(curl -s https://api.github.com/repos/rabbitmq/cluster-operator/contents/observability/prometheus/rules/rabbitmq-per-object | jq -r '.[].download_url'); do   kubectl apply -n prometheus -f $file; done
```

In order for these to work we also need to make sure that they match the `ruleSelector` from the Prometheus deployment. For Genestack deployments run:

```bash
kubectl get prometheusrule -n prometheus -o name | xargs -I {} kubectl label -n prometheus {} release=kube-prometheus-stack --overwrite
```

This gets all the rules in the `prometheus` namespace and applies the `release=kube-prometheus-stack` label. At this point the alerts will be configured in Prometheus.
