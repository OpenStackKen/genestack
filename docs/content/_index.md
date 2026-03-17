---
title: "Genestack Documentation"
weight: 10
description: "Reference, design, deployment, and operations documentation for Genestack."
hero:
  eyebrow: "Shared Docs"
  heading: "Build, operate, and extend Genestack"
  lead: "Reference material for architecture, deployment, operations, and onboarding."
  primary:
    text: "Start with Overview"
    url: "/overview/"
  secondary:
    text: "Go to Deployment Guide"
    url: "/deployment-guide/"
home_sections:
  - title: "Core Guides"
    description: "Primary documentation entry points."
    items:
      - title: "Overview"
        url: "/overview/"
        description: "Platform concepts, architecture, and component overviews."
      - title: "Design Guide"
        url: "/design-guide/"
        description: "Cloud design decisions, regional structure, resiliency, and platform architecture guidance."
      - title: "Deployment Guide"
        url: "/deployment-guide/"
        description: "Environment bring-up, platform prerequisites, and service deployment workflows."
      - title: "Operations Guide"
        url: "/operational-guide/"
        description: "Day-two operations, troubleshooting, lifecycle tasks, and operational playbooks."
  - title: "Additional Guides"
    description: "Audience-specific entry points and supporting reference material."
    items:
      - title: "Cloud Onboarding"
        url: "/cloud-onboarding/"
        description: "End-user onboarding for CLI setup, compute, networking, storage, and common OpenStack workflows."
      - title: "Secure by Design"
        url: "/design-guide/security/"
        description: "Secure development and layered security guidance that complements deployment and operations."
external_resources:
  - title: "Join the community on Discord"
    url: "https://discord.gg/2mN5yZvV3a"
  - title: "Learn more about Rackspace OpenStack"
    url: "https://www.rackspace.com/solve/return-openstack"
---
Genestack combines Kubernetes, OpenStack, and supporting infrastructure into a
single operations and deployment workflow.

The `/docs` tree is the canonical shared content source for both the local Hugo
site and downstream consumers such as `genestack-site`.
