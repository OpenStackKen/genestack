# Docs Reorganization Plan

## Summary

Reorganize `/docs/content` so the Hugo/Docsy sidebar is driven by the
filesystem and page metadata, with the primary goal of making the content more
organized, more maintainable, and easier to navigate.

Matching the old MkDocs site is no longer a primary requirement. Any suggestions
that would make the navigation resemble the old MkDocs layout should be treated
as optional follow-up evaluation after the major structural changes are done.

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
- `/docs/content/design-guide/security/_index.md`
- `/docs/content/design-guide/security/standards/_index.md`

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

Within `security`, the order should be:

- `Layered Security`
- `Securing Private Cloud Infrastructure`
- `Security Standards`

Within `security/standards`, the order should be:

- `NIST SP 800-53`
- `PCI DSS`
- `CIS Controls`
- `FedRAMP`
- `GDPR`
- `ISO 27001`

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
- `/docs/content/deployment-guide/getting-the-code.md`
- `/docs/content/deployment-guide/hyperconverged-lab.md`
- `/docs/content/deployment-guide/open-infrastructure/`
  - `bootstrap-the-environment.md`
  - `secrets/`
  - `kubernetes/`
  - `storage/`
  - `infrastructure/`
  - `openstack/`
  - `observability/`

Recommended top-level order:

- `Deployment Guide`
- `Getting the Code`
- `Hyperconverged Lab Deployment`
- `Open Infrastructure`

Recommended internal structure:

- under `kubernetes/`:
  - `overview.md`
  - `providers/`
  - `install-kube-ovn.md`
  - `post-deployment/`
- under `openstack/`:
  - `overview.md`
  - `block-storage/`
  - `compute-kit/`
  - `dashboards/`
  - `metering/`
  - `dnsaas/`
  - `trove/`
- rename the current observability-style deployment grouping to `monitoring/`
  only if that proves clearer after the major structural changes are complete

Immediate next steps from the current tree:

1. Evaluate whether `observability/` should be renamed to `monitoring/` after
   the larger parent/child restructuring is complete.
2. Evaluate later whether `secrets/` should remain its own subsection under
   `open-infrastructure/` or be folded further under `infrastructure/`.
3. Review the remaining root-level OpenStack pages after the current subgroup
   move and decide whether any of them should be grouped further, or kept flat.
4. Repair the remaining stale internal Deployment Guide links that still point
   at historical flat paths outside the scope of the current move.

## Operations Guide

This is the section that needs the largest reorganization to make it clearer
and more task-oriented.

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

This structure is more task-oriented than the current broader buckets.

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

## Optional Follow-Up

After the major structural changes are complete, review whether any remaining
navigation should be adjusted to resemble the old MkDocs site more closely.
Those parity-oriented changes are optional and should not block the main
reorganization work.

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
