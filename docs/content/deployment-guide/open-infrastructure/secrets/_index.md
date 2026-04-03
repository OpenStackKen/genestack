---
title: "Secrets and Key Management"
weight: 60
type: docs
simple_list: true
description: "Secret management and delivery with Sealed Secrets."
cascade:
  - type: docs
---

> [!WARNING]
>
> **EXPERIMENTAL: STILL UNDER DEVELOPMENT**
>
> None of the vault components are required to run a Genestack environment.

[Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) is a Kubernetes-native solution for securely storing and managing sensitive information within Kubernetes Secrets. It ensures secure secret management by encrypting Kubernetes Secrets and storing them as SealedSecret resources, which can only be decrypted by the cluster itself.

Sealed Secrets utilizes public-key cryptography to encrypt secrets, enabling safe storage in your version control system.
