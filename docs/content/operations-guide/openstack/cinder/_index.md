---
title: "Block Storage"
description: "Managing Cinder"
weight: 30
---

[Cinder](https://docs.openstack.org/cinder/latest/) serves as the cornerstone of storage management in OpenStack's cloud computing ecosystem. It provides a robust block storage service to provision and manage persistent storage volumes for virtual machines. Cinder  allows administrators to leverage various storage backends, from basic local disk arrays ([cinder-lvm](https://docs.openstack.org/cinder/latest/configuration/block-storage/drivers/lvm-volume-driver.html)) to the latest sophisticated NVMe-over-Fabric ([NVMe-oF](https://docs.openstack.org/cinder/latest/configuration/block-storage/drivers/spdk-volume-driver.html)) IP storage area networks (SANs). Cinder ensures that cloud workloads have reliable, scalable access to storage resources.
