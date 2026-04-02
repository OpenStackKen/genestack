---
title: "Metrics"
description: "Monitoring and observation of Barbican metrics."
weight: 2
---

The Barbican exporter allows monitoring of OpenStack's Key Management Service (Barbican) by exposing metrics to Prometheus. It collects metrics about secrets, containers, and other Barbican-specific resources.

#### Install the Barbican Exporter Helm Chart

```shell
bin/install-barbican-exporter.sh
```

> [!TIP]
>
> If the installation is successful, you should see the barbican-exporter pod running in the openstack namespace.
