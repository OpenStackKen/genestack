---
title: "Core Services"
weight: 70
type: docs
simple_list: true
description: "Nova, Placement, Neutron integration, and compute deployment components."
cascade:
  - type: docs
---

The core services in OpenStack encompass a "Compute Kit" providing the critical services that power the computational infrastructure of a cloud environment.

- **Nova** is the compute service that manages and orchestrates the lifecycle of virtual machines (VMs), handling tasks such as instance creation, scheduling, and termination.
- **Neutron** provides the networking service, enabling flexible network connectivity and addressing within the cloud, including support for complex networking configurations like VLANs, VXLANs, and advanced routing.
- **Placement** is a resource tracking service that ensures optimal allocation of compute, storage, and network resources across the cloud.

Together, Nova, Neutron, and Placement form the backbone of the OpenStack Compute Kit, enabling the efficient and scalable operation of cloud instances. In this document, we will explore how these services can be deployed using Genestack.

> [!IMPORTANT]
> **External Ceph Storage Backend**
>
> If Nova will be deployed with an external Ceph storage backend, review the
> [OpenStack Compute Ceph Store](/operational-guide/openstack-compute-ceph-store/) operator
> documentation for additional steps and setup.

## Demo

[![asciicast](https://asciinema.org/a/629813.svg)](https://asciinema.org/a/629813)

## Services
