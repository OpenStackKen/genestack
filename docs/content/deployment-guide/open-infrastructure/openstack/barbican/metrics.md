---
<<<<<<<< HEAD:docs/content/deployment-guide/open-infrastructure/openstack/barbican/metrics.md
title: "Metrics"
description: "Monitoring and observation of Barbican metrics."
weight: 2
========
title: "Barbican Exporter"
weight: 130
>>>>>>>> main:docs/content/deployment-guide/open-infrastructure/observability/exporters/openstack/barbican.md
---

The Barbican exporter allows monitoring of OpenStack's Key Management Service (Barbican) by exposing metrics to Prometheus. It collects metrics about secrets, containers, and other Barbican-specific resources.

<<<<<<<< HEAD:docs/content/deployment-guide/open-infrastructure/openstack/barbican/metrics.md
#### Install the Barbican Exporter Helm Chart
========
### Install the Barbican Exporter Helm Chart
>>>>>>>> main:docs/content/deployment-guide/open-infrastructure/observability/exporters/openstack/barbican.md

```shell
bin/install-barbican-exporter.sh
```

<<<<<<<< HEAD:docs/content/deployment-guide/open-infrastructure/openstack/barbican/metrics.md
> [!TIP]
>
> If the installation is successful, you should see the barbican-exporter pod running in the openstack namespace.
========
> [!SUCCESS]
>
> If the installation is successful, you should see the barbican-exporter pod running in the openstack namespace.
>>>>>>>> main:docs/content/deployment-guide/open-infrastructure/observability/exporters/openstack/barbican.md
