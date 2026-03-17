# Docs Reorganization Plan

## Summary

Reorganize `/docs/content` so the Hugo/Docsy sidebar is driven by the
filesystem and page metadata, while making the resulting navigation behave more
like the old MkDocs site.

This plan intentionally avoids a custom sidebar manifest. The source of truth
for navigation should be:

- directory structure for hierarchy
- `_index.md` for section identity and section order
- front matter `weight` for ordering within each section

This keeps navigation content-owned and portable for downstream use by
`genestack-site`.

## Navigation Model

- Use directories to represent real content groupings.
- Use each section `_index.md` to define:
  - `title`
  - `description`
  - `weight`
  - optional `cascade`
- Use each leaf page front matter to define:
  - `title`
  - `weight`
- Keep ordinary article bodies plain Markdown.
- Let Docsy render the sidebar from the content tree.

## Design Guide

This section is now the reference model for the rest of the site and is
effectively complete for the current reorganization pass.

Filesystem structure:

- `/docs/content/design-guide/_index.md`
- `/docs/content/design-guide/cloud-design/_index.md`
- `/docs/content/design-guide/design-notes/_index.md`

Target order:

- `Genestack SDLC`
- `Secure Development`
- `Cloud Design`
- `Infrastructure Design Notes`
- `Genestack Documentation Standards and Style Guide`

Within `cloud-design`, the order should be:

- `Cloud Topology`
- `Regions`
- `Availability Zones`
- `Host Aggregates`

Within `design-notes`, the order should be:

- `Accelerated Computing`
- `Disaster Recovery`
- `Bare-Metal Provisioning`

Within `accelerated-computing`, the order should be:

- `Overview`
- `Infrastructure`

## Cloud Onboarding

Recommended structure:

- `/docs/content/cloud-onboarding/_index.md`
- `/docs/content/cloud-onboarding/object-store/_index.md`

Move the object-store pages under `object-store/`:

- `storage-object-store-openstack-cli.md`
- `storage-object-store-swift-cli.md`
- `storage-object-store-s3-cli.md`
- `storage-object-store-skyline-gui.md`
- `storage-object-store-swift-3rd-party.md`

Ordering goal:

- core onboarding workflows first
- object-store content grouped together after the main compute/network/storage
  entry points

## Deployment Guide

Recommended target hierarchy:

- `/docs/content/deployment-guide/_index.md`
- `/docs/content/deployment-guide/getting-started/`
- `/docs/content/deployment-guide/open-infrastructure/`
  - `kubernetes/`
  - `storage/`
  - `infrastructure/`
  - `openstack/`
  - `monitoring/`

Recommended top-level order:

- `What is Genestack?` or equivalent intro
- `Getting Started`
- `Open Infrastructure`

Recommended internal structure:

- under `kubernetes/`:
  - `providers/`
  - `container-network-interface/`
  - `post-deployment/`
- under `openstack/`, optionally `openstack-services/` with subgroups:
  - `block-storage/`
  - `compute-kit/`
  - `dashboards/`
  - `metering/`
  - `dnsaas/`
  - `trove/`
- rename the current observability-style deployment grouping to `monitoring/`
  if the goal is to align more closely with the old MkDocs navigation language

Immediate next steps from the current tree:

1. Introduce an `open-infrastructure/` parent and move the current
   `infrastructure/`, `kubernetes/`, `storage/`, `openstack/`, and
   `observability/` subsections under it.
2. Rename `observability/` to `monitoring/` so the top-level terminology
   matches the old MkDocs information scent more closely.
3. Decide whether `secrets/` remains a first-class subsection or gets folded
   under `infrastructure/` as supporting platform material.
4. Subdivide `kubernetes/` into:
   - `providers/`
   - `container-network-interface/`
   - `post-deployment/`
5. Subdivide `openstack/` into service groupings where the grouping adds
   meaningful navigation value:
   - `block-storage/`
   - `compute-kit/`
   - `dashboards/`
   - `metering/`
   - `dnsaas/`
   - `trove/`

## Operations Guide

This is the section that needs the largest reorganization if the goal is to
make Docsy navigation behave like the old MkDocs site.

Recommended target hierarchy:

- `/docs/content/operational-guide/_index.md`
- `genestack/`
- `resource-metering/`
- `infrastructure/`
  - `kubernetes/`
  - `ovn/`
  - `mariadb/`
  - `gateway-api/`
- `observability/`
- `upgrades/`
- `openstack/`
  - `cli-access/`
  - `block-storage/`
  - `compute/`
  - `quota-management/`
  - `images/`
  - `identity/`
  - `networking/`
  - `containers/`
  - `loadbalancers/`
  - `object-storage/`
  - `reservation/`
  - `backup-restore/`
  - `databases/`

This structure is more task-oriented and closer to the old MkDocs
information scent than the current broader buckets.

## Overview

Keep this section mostly as-is.

Use `weight` to maintain a clear order for foundational pages such as:

- architecture
- components
- product matrix
- release notes

## Info

Keep `/docs/content/info` as maintainer and contract documentation, not as a
first-class published product-docs section.

If it remains published locally, it should still be low-weight and excluded
from normal product-navigation emphasis.

## Execution Order

Recommended implementation order:

1. Deployment Guide
2. Cloud Onboarding
3. Operations Guide

This keeps the highest-risk and broadest restructuring last.

## Rules For Moves

- Set `weight` explicitly on every `_index.md`.
- Set `weight` explicitly on moved leaf pages inside grouped sections.
- Keep article bodies plain Markdown and presentation-neutral.
- Rebuild after each coherent reorganization step so the generated site at
  `:1313` reflects the current tree.

## Recommendation

The preferred long-term model is:

- filesystem defines hierarchy
- `_index.md` defines section identity and section order
- leaf front matter defines page order
- Docsy renders navigation from the content tree
- no custom sidebar manifest unless the filesystem model proves insufficient
