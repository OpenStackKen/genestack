---
title: "OpenStack Exporter"
weight: 370
aliases:
  - /openstack-exporter/
---

# OpenStack Exporter

OpenStack Exporter is used to monitor and collect metrics from OpenStack services. It provides visibility into various OpenStack components and their performance metrics through Prometheus.

## Prerequisites

- Kubernetes cluster
- Prometheus Operator installed
- Access to OpenStack Keystone service
- Helm (if using Helm installation)

## Installation

### 1. Create Authentication Secret

First, create the Keystone authentication secret in the prometheus namespace:

```shell
kubectl --namespace prometheus \
        create secret generic keystone-auth-openstack-exporter \
        --type Opaque \
        --from-literal=AUTH_URL="http://keystone-api.openstack.svc.cluster.local:5000/v3" \
        --from-literal=USERNAME="admin" \
        --from-literal=PASSWORD="$(kubectl get secret keystone-admin -n openstack -o jsonpath={.data.password} | base64 -d -w0)" \
        --from-literal=USER_DOMAIN_NAME="Default" \
        --from-literal=PROJECT_NAME="admin" \
        --from-literal=PROJECT_DOMAIN_NAME="Default"
```

> [!NOTE]
>
> the openstack exporter by just running the install script - `/opt/genestack/bin/install-openstack-exporter.sh`

```shell
```shell
#!/bin/bash
set -e  # Exit on error

# Variables
CHART_DIR="/opt/genestack/base-helm-configs/openstack-api-exporter-chart"
NAMESPACE="prometheus"
RELEASE_NAME="openstack-exporter"

# Check if chart directory exists
if [ ! -d "${CHART_DIR}" ]; then
    echo "Chart directory ${CHART_DIR} does not exist!"
    exit 1
fi

# Function to find an unused port
find_unused_port() {
    local port=49152
    while :; do
        if ! kubectl get svc --all-namespaces -o jsonpath='{range .items[*]}{.spec.ports[*].port}{"\n"}{end}' | grep -q "${port}$"; then
            echo "$port"
            return 0
        fi
        ((port++))
        if [ $port -gt 65535 ]; then
            echo "No unused port found in range 49152-65535" >&2
            exit 1
        fi
    done
}

# Ensure namespace exists
if ! kubectl get namespace ${NAMESPACE} >/dev/null 2>&1; then
    echo "Namespace ${NAMESPACE} does not exist. Creating..."
    kubectl create namespace ${NAMESPACE}
fi

# Check if release already exists
if helm list -n ${NAMESPACE} | grep -q ${RELEASE_NAME}; then
    echo "Release ${RELEASE_NAME} already exists!"
    exit 1
fi

# Find and set dynamic values
DYNAMIC_PORT=$(find_unused_port)
DYNAMIC_TAG="sha-7951e2c"
echo "Using dynamic port: $DYNAMIC_PORT and tag: $DYNAMIC_TAG"

# Install Helm chart with dynamic values
echo "Installing Helm chart..."
helm install ${RELEASE_NAME} ${CHART_DIR} \
    --namespace ${NAMESPACE} \
    --set image.tag=${DYNAMIC_TAG} \
    --set service.port=${DYNAMIC_PORT} || {
        echo "Helm installation failed!"
        exit 1
    }

# Verify deployment
echo "Verifying deployment..."
kubectl get pods -n ${NAMESPACE}
kubectl get svc -n ${NAMESPACE}
kubectl get servicemonitor -n ${NAMESPACE}

echo "Installation complete with port $DYNAMIC_PORT!"
```
```

> [!TIP]

If the installation is successful, you should see the exporter pod in the prometheus namespace.

``` shell
kubectl get pods -n openstack -l app=openstack-exporter
```

## Test and Verify
Can verify the metrics by just port-forwarding and curl command.
Which port the service is running can be seen by the following command,
```shell
kubectl get svc -n prometheus | grep openstack-exporter
```

Port Forwarding of openstack-exporter service to see the metrics:-
``` shell
kubectl port-forward svc/openstack-exporter -n prometheus 9180:<service-port>
```
Run Curl command in another window - curl localhost:9180/metrics


Also we can we can see the metrics on the prometheus GUI under the target path using following command,

```shell
kubectl port-forward svc/kube-prometheus-stack-prometheus -n prometheus 9090:9090
```

open the link on a browser - http://localhost:9090/targets
And select the serviceMonitor as "serviceMonitor/prometheus/openstack-exporter/0", Then will see it is showing up and all the details about it.
