---
title: "Load Balancers"
description: "Working with Octavia Load Balancers"
weight: 90
---

[Octavia](https://docs.openstack.org/octavia/latest/) provides Load Balancing as a Service (LBaaS) for OpenStack. It is comprised of three major components:

### Amphorae

These handle the load balancing services. Amphorae are the individual virtual machines, containers, or bare metal servers responsible for delivering load balancing services to tenant application environments. They handle the actual traffic distribution and processing.

### Controller

This serves as the “brains” of Octavia and consists of several sub-components:

- API Controller: This runs Octavia’s API, receiving and processing API requests.
- Controller Worker: This receives sanitized API commands from the API controller and performs the necessary actions to fulfill the requests.
- Health Manager: This monitors the status and health of individual amphorae, ensuring they are running properly. It also handles failover events in case of amphorae failures.
- Housekeeping Manager: This manages the rotation of amphora certificates and removes outdated (deleted) database records.
- Driver Agent: This component receives updates on status and statistics from the provider drivers, enabling effective coordination between Octavia and the underlying load balancing infrastructure.

### Network

This component handles the network environment necessary for load balancing operations. It includes the setup of the load balancer network interface on the amphorae and facilitates connectivity between amphorae, tenant networks, and external networks
