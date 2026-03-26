---
title: "Architecture Mermaid Test"
weight: 999
type: docs
description: "Temporary test page for evaluating an architecture-beta Mermaid version of the infrastructure overview."
---

This page is a testbed for replacing the static infrastructure overview image with a Mermaid `architecture-beta` diagram.

## Proposed Diagram

```mermaid
architecture-beta
  group access(cloud)[External Access]
  group api(cloud)[Kubernetes API Components]
  group platform(cloud)[CNCF Kubernetes and Operators]
  group runtime(server)[Node Runtime]
  group base(server)[Host Foundation]

  service metallb(internet)[MetalLB] in access
  service exposed_api(server)[Exposed Kubernetes API] in access

  service kube_apiserver(server)[kube-apiserver] in api
  service kube_proxy(server)[kube-proxy] in api
  service coredns(server)[CoreDNS] in api
  service nginx_gateway(server)[Nginx Gateway Ctrl] in api
  service registry(disk)[Registry] in api
  service cert_manager(shield)[Cert-Manager] in api
  service helm(cli)[Helm] in api
  service calico_controller(server)[Calico Controller] in api
  service metal3(database)[Metal3.io CRD] in api
  service prometheus(database)[Prometheus / Thanos] in api

  service kubelet(server)[kubelet] in platform
  service etcd(database)[etcd] in platform
  service cni(network)[CNI: Calico / KubeOVN] in platform
  service local_path(disk)[Local Path Provisioner] in platform
  service ceph(storage)[CSI: Ceph] in platform

  service containerd(server)[containerd] in runtime

  service os(server)[Operating System] in base
  service hw(server)[Intel/AMD x86_64 Platforms] in base

  metallb:R --> L:exposed_api
  exposed_api:B --> T:kube_apiserver

  helm:B --> T:kube_apiserver
  kube_apiserver:L --> R:kube_proxy
  kube_apiserver:B --> T:kubelet
  kube_apiserver:B --> T:etcd
  kube_apiserver:B --> T:cni
  kube_apiserver:R --> L:coredns
  kube_apiserver:R --> L:nginx_gateway
  kube_apiserver:R --> L:cert_manager
  kube_apiserver:R --> L:prometheus
  kube_apiserver:R --> L:metal3
  calico_controller:B --> T:cni

  kubelet:B --> T:containerd
  cni:B --> T:os
  local_path:B --> T:os
  ceph:B --> T:os
  containerd:B --> T:os
  os:B --> T:hw
```

## Notes

- This intentionally favors a layered architecture view over pixel-for-pixel parity with the current SVG.
- The goal is to preserve the main system relationships while using Mermaid's native architecture notation.
