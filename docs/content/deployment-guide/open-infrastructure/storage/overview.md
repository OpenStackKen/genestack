---
title: "Overview"
weight: 10
---
For the basic needs of our Kubernetes environment, we need some basic persistent storage. Storage, like anything good in life,
is a choose your own adventure ecosystem, so feel free to ignore this section if you have something else that satisfies the need.

## Deploying Your Persistent Storage

The basis needs of Genestack are the following storage classes

| Storage Type | Description |
|--------------|-------------|
| general | A general storage cluster which is set as the deault |
| general-multi-attach | A multi-read/write storage backend |

These `StorageClass` types are needed by various systems; however, how you get to these storage classes is totally up to you.
The following sections provide a means to manage storage and provide our needed `StorageClass` types. While there may be many
persistent storage options, not all of them are needed.

| Type | Supported Storage Options |
|------|---------------------------|
| Internal | [Longhorn](/deployment-guide/open-infrastructure/storage/longhorn/) |
| Internal | [TopoLVM](/deployment-guide/open-infrastructure/storage/topolvm/) |
| Internal | [Ceph Rook Operator](/deployment-guide/open-infrastructure/storage/ceph-rook-internal/) |
| External | [NFS](/deployment-guide/open-infrastructure/storage/nfs-external/) |
| External | [Add a Ceph cluster with rook-ceph](/deployment-guide/open-infrastructure/storage/ceph-rook-external/) |
| External | [Using other CSI drivers](/deployment-guide/open-infrastructure/storage/external-block/) |

## Storage Deployment Demo

[![asciicast](https://asciinema.org/a/629785.svg)](https://asciinema.org/a/629785)
