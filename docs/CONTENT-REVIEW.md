# Content Review After Rebase

This file tracks branch-vs-`main` content differences that should be
reviewed after each rebase.

The goal is not to list every filesystem move or asset relocation. The goal is
to capture the content areas where:

- the canonical path changed
- the navigation model changed
- the rendered title or section semantics changed
- a page was materially rewritten
- a conflict was resolved in favor of branch-specific content
- generated content is now produced differently from `main`

## Current baseline

- `origin/main`: `502afb1`
- `codex/docs-refactor`: `f530c71`

## How to update this file after a rebase

1. Compare `origin/main...HEAD` for `/docs/content`.
2. Ignore pure image moves and other non-content relocations unless they change
   page meaning.
3. Update the review buckets below with:
   - new pages in `main` that need to be mapped into the refactored tree
   - pages whose prose changed on both sides
   - files that required manual conflict resolution
   - generated pages whose generation path or emitted content changed
4. Remove items once they are explicitly reviewed and no longer need follow-up.

## Priority review items

- [ ] [docs/content/operational-guide/openstack/keystone-ldap.md](/Users/ken/Dev/genestack/docs/content/operational-guide/openstack/keystone-ldap.md)
  Main-path source: [docs/openstack-keystone-ldap.md](/Users/ken/Dev/genestack/docs/openstack-keystone-ldap.md) on `main`
  Reason: this page required a manual rebase conflict resolution. The branch
  kept the Hugo-native refactored content instead of the older MkDocs-era
  include/admonition block from `main`.

- [ ] [docs/content/overview/release-notes.md](/Users/ken/Dev/genestack/docs/content/overview/release-notes.md)
  Main-path source: [docs/release-notes.md](/Users/ken/Dev/genestack/docs/release-notes.md) on `main`
  Reason: the page is now generated into the Hugo content tree from the new
  `reno -> pandoc -> Markdown` containerized workflow. The content is no longer
  the old static stub from `main`.

- [ ] [docs/content/overview/product-matrix.md](/Users/ken/Dev/genestack/docs/content/overview/product-matrix.md)
  Main-path source: [docs/product-matrix.md](/Users/ken/Dev/genestack/docs/product-matrix.md) on `main`
  Reason: this page moved into the Hugo overview section and should be checked
  whenever `main` changes the old MkDocs-era product matrix source or its
  generation expectations.

## Section-level review buckets

These sections were reorganized enough that upstream content changes on `main`
may now need manual mapping into a different canonical location here.

### Design Guide

- [ ] [docs/content/design-guide/_index.md](/Users/ken/Dev/genestack/docs/content/design-guide/_index.md)
- [ ] [docs/content/design-guide/cloud-design/_index.md](/Users/ken/Dev/genestack/docs/content/design-guide/cloud-design/_index.md)
- [ ] [docs/content/design-guide/design-notes/_index.md](/Users/ken/Dev/genestack/docs/content/design-guide/design-notes/_index.md)
- [ ] [docs/content/design-guide/security/_index.md](/Users/ken/Dev/genestack/docs/content/design-guide/security/_index.md)
- [ ] [docs/content/design-guide/standards.md](/Users/ken/Dev/genestack/docs/content/design-guide/standards.md)

Main-path sources to compare against when upstream edits land:

- [docs/openstack-cloud-design-az.md](/Users/ken/Dev/genestack/docs/openstack-cloud-design-az.md)
  -> [docs/content/design-guide/cloud-design/availability-zones.md](/Users/ken/Dev/genestack/docs/content/design-guide/cloud-design/availability-zones.md)
- [docs/openstack-cloud-design-ha.md](/Users/ken/Dev/genestack/docs/openstack-cloud-design-ha.md)
  -> [docs/content/design-guide/cloud-design/host-aggregates.md](/Users/ken/Dev/genestack/docs/content/design-guide/cloud-design/host-aggregates.md)
- [docs/openstack-cloud-design-regions.md](/Users/ken/Dev/genestack/docs/openstack-cloud-design-regions.md)
  -> [docs/content/design-guide/cloud-design/regions.md](/Users/ken/Dev/genestack/docs/content/design-guide/cloud-design/regions.md)
- [docs/openstack-cloud-design-topology.md](/Users/ken/Dev/genestack/docs/openstack-cloud-design-topology.md)
  -> [docs/content/design-guide/cloud-design/topology.md](/Users/ken/Dev/genestack/docs/content/design-guide/cloud-design/topology.md)
- [docs/openstack-cloud-design-dr.md](/Users/ken/Dev/genestack/docs/openstack-cloud-design-dr.md)
  -> [docs/content/design-guide/design-notes/disaster-recovery.md](/Users/ken/Dev/genestack/docs/content/design-guide/design-notes/disaster-recovery.md)
- [docs/openstack-cloud-design-genestack-infra.md](/Users/ken/Dev/genestack/docs/openstack-cloud-design-genestack-infra.md)
  -> [docs/content/design-guide/design-notes/bare-metal.md](/Users/ken/Dev/genestack/docs/content/design-guide/design-notes/bare-metal.md)
- [docs/accelerated-computing-overview.md](/Users/ken/Dev/genestack/docs/accelerated-computing-overview.md)
  -> [docs/content/design-guide/design-notes/accelerated-computing/accelerated-computing-overview.md](/Users/ken/Dev/genestack/docs/content/design-guide/design-notes/accelerated-computing/accelerated-computing-overview.md)
- [docs/accelerated-computing-infrastructure.md](/Users/ken/Dev/genestack/docs/accelerated-computing-infrastructure.md)
  -> [docs/content/design-guide/design-notes/accelerated-computing/accelerated-computing-infrastructure.md](/Users/ken/Dev/genestack/docs/content/design-guide/design-notes/accelerated-computing/accelerated-computing-infrastructure.md)
- [docs/security-introduction.md](/Users/ken/Dev/genestack/docs/security-introduction.md)
  -> [docs/content/design-guide/security/_index.md](/Users/ken/Dev/genestack/docs/content/design-guide/security/_index.md)
- [docs/security-lifecycle.md](/Users/ken/Dev/genestack/docs/security-lifecycle.md)
  -> [docs/content/design-guide/security/security-lifecycle.md](/Users/ken/Dev/genestack/docs/content/design-guide/security/security-lifecycle.md)
- [docs/security-stages.md](/Users/ken/Dev/genestack/docs/security-stages.md)
  -> [docs/content/design-guide/security/security-stages.md](/Users/ken/Dev/genestack/docs/content/design-guide/security/security-stages.md)
- [docs/security-summary.md](/Users/ken/Dev/genestack/docs/security-summary.md)
  -> [docs/content/design-guide/security/security-summary.md](/Users/ken/Dev/genestack/docs/content/design-guide/security/security-summary.md)
- [docs/documentation-standards.md](/Users/ken/Dev/genestack/docs/documentation-standards.md)
  -> [docs/content/design-guide/standards.md](/Users/ken/Dev/genestack/docs/content/design-guide/standards.md)

### Deployment Guide

- [ ] [docs/content/deployment-guide/_index.md](/Users/ken/Dev/genestack/docs/content/deployment-guide/_index.md)
- [ ] [docs/content/deployment-guide/getting-the-code.md](/Users/ken/Dev/genestack/docs/content/deployment-guide/getting-the-code.md)
- [ ] [docs/content/deployment-guide/hyperconverged-lab.md](/Users/ken/Dev/genestack/docs/content/deployment-guide/hyperconverged-lab.md)
- [ ] [docs/content/deployment-guide/open-infrastructure/_index.md](/Users/ken/Dev/genestack/docs/content/deployment-guide/open-infrastructure/_index.md)

Review note:
- this is the largest content and navigation reorganization on the branch
- upstream edits to old flat deployment files on `main` need to be mapped into
  the nested `open-infrastructure/` tree here, not compared by path alone

Representative mappings:

- [docs/build-test-envs.md](/Users/ken/Dev/genestack/docs/build-test-envs.md)
  -> [docs/content/deployment-guide/hyperconverged-lab.md](/Users/ken/Dev/genestack/docs/content/deployment-guide/hyperconverged-lab.md)
- [docs/genestack-getting-started.md](/Users/ken/Dev/genestack/docs/genestack-getting-started.md)
  -> [docs/content/deployment-guide/getting-the-code.md](/Users/ken/Dev/genestack/docs/content/deployment-guide/getting-the-code.md)
- [docs/infrastructure-overview.md](/Users/ken/Dev/genestack/docs/infrastructure-overview.md)
  -> [docs/content/deployment-guide/open-infrastructure/infrastructure/overview.md](/Users/ken/Dev/genestack/docs/content/deployment-guide/open-infrastructure/infrastructure/overview.md)
- [docs/k8s-overview.md](/Users/ken/Dev/genestack/docs/k8s-overview.md)
  -> [docs/content/deployment-guide/open-infrastructure/kubernetes/overview.md](/Users/ken/Dev/genestack/docs/content/deployment-guide/open-infrastructure/kubernetes/overview.md)
- [docs/storage-overview.md](/Users/ken/Dev/genestack/docs/storage-overview.md)
  -> [docs/content/deployment-guide/open-infrastructure/storage/overview.md](/Users/ken/Dev/genestack/docs/content/deployment-guide/open-infrastructure/storage/overview.md)
- [docs/openstack-overview.md](/Users/ken/Dev/genestack/docs/openstack-overview.md)
  -> [docs/content/deployment-guide/open-infrastructure/openstack/overview.md](/Users/ken/Dev/genestack/docs/content/deployment-guide/open-infrastructure/openstack/overview.md)
- [docs/prometheus-monitoring-overview.md](/Users/ken/Dev/genestack/docs/prometheus-monitoring-overview.md)
  -> [docs/content/deployment-guide/open-infrastructure/observability/prometheus-monitoring-overview.md](/Users/ken/Dev/genestack/docs/content/deployment-guide/open-infrastructure/observability/prometheus-monitoring-overview.md)

### Cloud Onboarding

- [ ] [docs/content/cloud-onboarding/_index.md](/Users/ken/Dev/genestack/docs/content/cloud-onboarding/_index.md)
- [ ] object-store onboarding pages under [docs/content/cloud-onboarding](/Users/ken/Dev/genestack/docs/content/cloud-onboarding)

Review note:
- this section mostly moved into a subsection-aware Hugo tree
- check upstream edits for meaning changes, not just path changes

### Operational Guide

- [ ] [docs/content/operational-guide/_index.md](/Users/ken/Dev/genestack/docs/content/operational-guide/_index.md)
- [ ] [docs/content/operational-guide/lifecycle/_index.md](/Users/ken/Dev/genestack/docs/content/operational-guide/lifecycle/_index.md)
- [ ] [docs/content/operational-guide/observability/_index.md](/Users/ken/Dev/genestack/docs/content/operational-guide/observability/_index.md)
- [ ] [docs/content/operational-guide/openstack/_index.md](/Users/ken/Dev/genestack/docs/content/operational-guide/openstack/_index.md)
- [ ] [docs/content/operational-guide/ovn/_index.md](/Users/ken/Dev/genestack/docs/content/operational-guide/ovn/_index.md)

Review note:
- many old flat pages now live under narrower topical subsections
- compare by logical topic, not by path alone
- pay special attention to any upstream edits in observability, OVN, and
  OpenStack operator content

### Homepage and overview

- [ ] [docs/content/_index.md](/Users/ken/Dev/genestack/docs/content/_index.md)
- [ ] [docs/content/overview/_index.md](/Users/ken/Dev/genestack/docs/content/overview/_index.md)
- [ ] [docs/content/overview/genestack-architecture.md](/Users/ken/Dev/genestack/docs/content/overview/genestack-architecture.md)
- [ ] [docs/content/overview/genestack-components.md](/Users/ken/Dev/genestack/docs/content/overview/genestack-components.md)

Review note:
- these pages now sit inside Hugo section roots with explicit front matter and
  a branch-specific homepage layout
- upstream changes here can affect navigation and landing-page semantics

## What does not belong on this list

Do not expand this file with:

- pure image moves into `docs/content/assets/images`
- mechanical path-only moves with no prose or semantic change
- generated `public/` artifacts
- SCSS, layout, or build-tool changes unless they directly alter generated
  content that must be reviewed
