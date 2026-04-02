---
title: "Secure Development"
weight: 20
type: docs
description: "Secure development and layered security guidance for the platform."
simple_list: true
cascade:
  - type: docs
---

## Building a Secure and Resilient Cloud Environment

Our objective is to provide comprehensive guidelines for designing a secure and highly available cloud. Start by reviewing the recommendations outlined here to understand best practices for structuring your cloud infrastructure. With this foundation, we can establish security principles tailored to each critical component, ensuring they are robust and resilient against potential threats.

## Security by Design

GeneStack's multi-region and hybrid design, leveraging OpenStack and Kubernetes, provides a robust foundation for cloud-native workloads. By integrating layered security practices, you can enhance resilience against evolving threats. Regular audits, continuous improvement, and adherence to cloud-native security principles are vital for maintaining a secure environment.

Lets summarize our layered security approach in a table:

| Lifecycle Phase     | Infrastructure                       | Platform                             | Application                    | Data                                    |
| :---------:         | :----------------------------------: | :-----------------------------------:| :-----------------------------:|:---------------------------------------:|
| **Develop**         | Secure IaC, Validate Nodes           | Harden Platform Configs              | Secure code, container images  |Encrypt sensitive configuration and data |
| **Distribute**      | Validate Container/VM Images         | Secure API and configuration delivery| Verify container integrity     |Protect data during distribution         |
| **Deploy**          | Handen Deployed Nodes                | Enforce RBAC and security policies   | Apply runtime policies         |Encrypt data in transit                  |
| **Runtime**         | Monitor and Remediate Issues         | Detect API issues and misuse         | Monitor and secure workloads   |Protect sensitive data streams           |


By integrating these practices our security approach ensures comprehensive protection across the entire lifecycle of Genestack based OpenStack cloud.