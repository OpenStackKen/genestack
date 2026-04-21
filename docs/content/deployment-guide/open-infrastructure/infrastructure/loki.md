---
title: "Loki"
weight: 150
---
[Loki](https://grafana.com/oss/loki/) is a horizontally-scalable, highly-available, multi-tenant log aggregation system inspired by Prometheus. It is designed to be very cost-effective and easy to operate. It does not index the contents of the logs, but rather a set of labels for each log stream.

## Run the package deployment

Run the Loki deployment Script `/opt/genestack/bin/install-loki.sh`

```bash {include="bin/install-loki.sh"}
```
> [!TIP]

### Swift _(Recommended)_


> [!NOTE]
>
> If you plan on using **Swift** as a backend for log storage see the `loki-helm-swift-overrides.yaml.example` file in the `helm-configs/loki` directory.

```yaml {include="base-helm-configs/loki/loki-helm-swift-overrides.yaml.example"}
```
### S3


> [!NOTE]
>
> If you plan on using **S3** as a backend for log storage see the `loki-helm-s3-overrides.yaml.example` file in the `helm-configs/loki` directory.

```yaml {include="base-helm-configs/loki/loki-helm-s3-overrides.yaml.example"}
```
### MinIO


> [!NOTE]
>
> If you plan on using **MinIO** as a backend for log storage see the `loki-helm-minio-overrides.yaml.example` file in the `helm-configs/loki` directory.

```yaml {include="base-helm-configs/loki/loki-helm-minio-overrides.yaml.example"}
```
