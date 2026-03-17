---
title: "Post deployment Operations"
weight: 310
aliases:
  - /deployment-guide/k8s-taint/
  - /k8s-taint/
---
## Remove taint from our Controllers

In an environment with a limited set of control plane nodes removing the NoSchedule will allow you to converge the
openstack controllers with the k8s controllers.

``` shell
# Remote taint from control-plane nodes
kubectl taint nodes -l node-role.kubernetes.io/control-plane node-role.kubernetes.io/control-plane:NoSchedule-
```
