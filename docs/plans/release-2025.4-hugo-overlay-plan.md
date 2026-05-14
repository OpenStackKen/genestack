# Release 2025.4 Hugo Overlay Plan

## Document purpose

This is a living document for moving the `docs-refactor` Hugo site format onto
the `release-2025.4` line while walking back content that landed on `main`
after the `release-2025.4` split.

Execution model:

- the implementation branch is `release-2025.4`
- the content target is `release-2025.4`
- the Hugo/site-format source is `docs-refactor`

The target outcome is:

- keep the Hugo refactor in place
- keep the `docs-refactor` navigation, layout, render hooks, and stylistic
  conventions in place
- remove or roll back content that post-dates the `release-2025.4` split on
  `main`
- reapply the `release-2025.4`-specific content delta on top of that Hugo tree

This document should be updated as mappings are confirmed and as work is
completed.

## Baselines

- `main` / `release-2025.4` split point: `398f2b36`
- latest `main` point currently represented by `docs-refactor`:
  `0f70e3b55`
- working structural source: `docs-refactor`
- working release content source: `release-2025.4`

Important clarification:

- there is no local tag named `release-2025.4`
- the rollback baseline currently in use is the branch split between `main` and
  `release-2025.4`

## High-level strategy

1. Start from a copy of `docs-refactor`.
2. Treat that copy as the structural and stylistic source of truth.
3. Identify content that was added or changed on `main` after `398f2b36` and
   before `0f70e3b55`.
4. Walk those content changes back while keeping the Hugo site shape intact.
5. Reintroduce content required by `release-2025.4` that is absent from
   `docs-refactor`.
6. Overlay the `release-2025.4`-only content delta onto the Hugo tree.
7. Validate that the result matches the intended `release-2025.4` content set
   while preserving the Hugo refactor.

## Non-goals

- do not redesign the Hugo site beyond what already exists in `docs-refactor`
- do not perform editorial cleanup outside content rollback or required
  adaptation
- do not treat this as a generic MkDocs-to-Hugo migration from scratch
- do not preserve post-split `main` content unless it is explicitly wanted for
  `release-2025.4`

## Working rules

- preserve Hugo front matter, section placement, render hooks, admonition
  syntax, and navigation conventions from `docs-refactor`
- preserve `release-2025.4` content semantics where they differ from `main`
- prefer reversible changes
- keep structural replay separate from content rollback
- keep content rollback separate from `release-2025.4` overlay work

Recommended commit breakdown:

1. transplant `docs-refactor` onto `release-2025.4`
2. walk back `main`-only content changes to the split baseline
3. restore or add `release-2025.4`-required content not present in
   `docs-refactor`
4. overlay the `release-2025.4`-only content delta
5. fix navigation, links, and build fallout

## Content classes

Every affected page should be assigned one of these classes.

### `delete`

The page exists in `docs-refactor` only because it was added on `main` after
the `release-2025.4` split and should not be present in the `release-2025.4`
Hugo result.

### `revert`

The page exists in both lines, but the `docs-refactor` content reflects
post-split `main` changes. Keep the Hugo file and location, but replace the
body content with the split-baseline content.

### `manual merge`

The corresponding content exists in Hugo, but the page was split, merged, or
reshaped enough that a direct reverse patch is unsafe. These require guided
editing inside the Hugo target.

### `restore`

The content is required for `release-2025.4` but is absent from `docs-refactor`
and must be recreated in the Hugo tree.

### `overlay`

The page requires the `release-2025.4`-only delta after the rollback to the
split baseline is complete.

## Known `main`-side MkDocs-era content delta to walk back

Between `398f2b36` and `0f70e3b55`, `main` changed 28 content pages:

- 13 pages added
- 14 pages modified
- 1 page removed

### Added on `main`

- `docs/infrastructure-cert-manager.md`
- `docs/openstack-barbican-exporter.md`
- `docs/openstack-blazar-reservation-splitter.md`
- `docs/openstack-cinder-ceph-store.md`
- `docs/openstack-compute-ceph-store.md`
- `docs/openstack-designate.md`
- `docs/openstack-designate-prep.md`
- `docs/openstack-designate-neutron.md`
- `docs/openstack-designate-exporter.md`
- `docs/openstack-glance-ceph-store.md`
- `docs/openstack-keystone-ldap.md`
- `docs/openstack-trove.md`
- `docs/openstack-trove-mysql-images.md`

### Modified on `main`

- `docs/etcd-backup.md`
- `docs/genestack-components.md`
- `docs/import-grafana-dashboard.md`
- `docs/infrastructure-envoy-gateway-api.md`
- `docs/infrastructure-mariadb-ops.md`
- `docs/infrastructure-namespace.md`
- `docs/infrastructure-ovn-setup.md`
- `docs/k8s-kubespray-upgrade.md`
- `docs/monitoring-info.md`
- `docs/openstack-blazar.md`
- `docs/openstack-cinder.md`
- `docs/openstack-compute-kit.md`
- `docs/openstack-glance-images.md`
- `docs/openstack-glance.md`

### Removed on `main`

- `docs/infrastructure-argocd.md`

## Initial file classification

This section is the starting manifest. Update status and notes as the work is
performed.

| Source MkDocs page | Hugo target or action | Class | Status | Notes |
| --- | --- | --- | --- | --- |
| `docs/etcd-backup.md` | `docs/content/operations-guide/infrastructure/kubernetes/etcd-backup.md` | `revert` | `completed` | Split-era content restored while keeping Hugo front matter. |
| `docs/genestack-components.md` | `docs/content/overview/genestack-components.md` | `revert` | `completed` | ArgoCD restored and Trove entry removed. |
| `docs/import-grafana-dashboard.md` | `docs/content/operations-guide/observability/import-grafana-dashboard.md` | `revert` | `completed` | Split-era usage example restored. |
| `docs/infrastructure-argocd.md` | omit from Hugo result | `restore` | `not required` | The MkDocs page was not surfaced in navigation, so it is intentionally omitted from the `release-2025.4` Hugo target. |
| `docs/infrastructure-cert-manager.md` | `docs/content/deployment-guide/open-infrastructure/infrastructure/cert-manager.md` | `delete` | `completed` | Removed from Hugo tree. |
| `docs/infrastructure-envoy-gateway-api.md` | `docs/content/deployment-guide/open-infrastructure/infrastructure/gateway/envoy-gateway-api.md` | `revert` | `completed` | Post-split DNS challenge expansion removed. |
| `docs/infrastructure-mariadb-ops.md` | `docs/content/operations-guide/infrastructure/mariadb/_index.md` | `manual merge` | `completed` | Galera migration appendix removed and heading restored. |
| `docs/infrastructure-namespace.md` | `docs/content/deployment-guide/open-infrastructure/infrastructure/namespace.md` | `revert` | `completed` | Skyline note removed. |
| `docs/infrastructure-ovn-setup.md` | `docs/content/deployment-guide/open-infrastructure/infrastructure/ovn-setup.md` | `revert` | `completed` | Bonding and reconfiguration additions removed. |
| `docs/k8s-kubespray-upgrade.md` | `docs/content/operations-guide/infrastructure/kubernetes/kubespray-upgrade.md` | `revert` | `completed` | Split-era playbook workflow restored. |
| `docs/monitoring-info.md` | `docs/content/operations-guide/observability/monitoring-info.md` | `revert` | `completed` | Barbican exporter paragraph removed. |
| `docs/openstack-barbican-exporter.md` | `docs/content/deployment-guide/open-infrastructure/openstack/barbican/metrics.md` | `delete` | `completed` | Removed from Hugo tree. |
| `docs/openstack-blazar-reservation-splitter.md` | `docs/content/operations-guide/openstack/blazar.md` | `manual merge` | `completed` | Removed from Hugo tree; post-split `main` addition only. |
| `docs/openstack-blazar.md` | `docs/content/deployment-guide/open-infrastructure/openstack/blazar.md` | `manual merge` | `completed` | Post-split filter instructions removed. |
| `docs/openstack-cinder-ceph-store.md` | `docs/content/operations-guide/openstack/cinder/cinder-ceph-store.md` | `delete` | `completed` | Removed from Hugo tree. |
| `docs/openstack-cinder.md` | `docs/content/deployment-guide/open-infrastructure/openstack/cinder/_index.md` | `manual merge` | `completed` | External Ceph addendum removed. |
| `docs/openstack-compute-ceph-store.md` | `docs/content/operations-guide/openstack/nova/nova-external-ceph.md` | `delete` | `completed` | Removed from Hugo tree. |
| `docs/openstack-compute-kit.md` | `docs/content/deployment-guide/open-infrastructure/openstack/compute/_index.md` | `manual merge` | `completed` | External Ceph addendum removed. |
| `docs/openstack-designate-exporter.md` | `docs/content/deployment-guide/open-infrastructure/observability/exporters/openstack/designate.md` | `delete` | `completed` | Removed from Hugo tree. |
| `docs/openstack-designate-neutron.md` | `docs/content/deployment-guide/open-infrastructure/openstack/designate/neutron.md` | `delete` | `completed` | Removed from Hugo tree. |
| `docs/openstack-designate-prep.md` | `docs/content/deployment-guide/open-infrastructure/openstack/designate/prepare.md` | `delete` | `completed` | Removed from Hugo tree. |
| `docs/openstack-designate.md` | `docs/content/deployment-guide/open-infrastructure/openstack/designate/_index.md` and `deploy.md` | `delete` | `completed` | Whole Designate feature set removed from Hugo tree. |
| `docs/openstack-glance-ceph-store.md` | `docs/content/operations-guide/openstack/glance/ceph-storage.md` | `delete` | `completed` | Removed from Hugo tree. |
| `docs/openstack-glance-images.md` | `docs/content/operations-guide/openstack/glance/image-creation.md` | `revert` | `completed` | Post-split image-format note removed. |
| `docs/openstack-glance.md` | `docs/content/deployment-guide/open-infrastructure/openstack/glance.md` | `manual merge` | `completed` | Split-era body restored while keeping Hugo page structure. |
| `docs/openstack-keystone-ldap.md` | `docs/content/operations-guide/openstack/keystone/ldap.md` | `delete` | `completed` | Removed from Hugo tree. |
| `docs/openstack-trove-mysql-images.md` | `docs/content/deployment-guide/open-infrastructure/openstack/trove/mysql.md` | `delete` | `completed` | Removed from Hugo tree. |
| `docs/openstack-trove.md` | `docs/content/deployment-guide/open-infrastructure/openstack/trove/_index.md` | `delete` | `completed` | Removed from Hugo tree. |

## Release-specific overlay

After the `main` rollback is complete, apply the `release-2025.4`-specific
delta.

Known `release-2025.4`-only content change relative to the split baseline:

- `docs/openstack-compute-kit-secrets.md`

Target Hugo page:

- `docs/content/deployment-guide/open-infrastructure/openstack/compute/secrets.md`

Required overlay content:

- fix the note title typo: `secretes` -> `secrets`
- add `nova-keystone-service-password`
- add `nova-keystone-test-password`
- rename secret `nova-ssh-keypair` -> `nova-ssh`
- rename keys `public_key` / `private_key` ->
  `public-key` / `private-key`

Status:

- completed on 2026-04-20 in
  `docs/content/deployment-guide/open-infrastructure/openstack/compute/secrets.md`

## Execution plan

### Phase 1: Structural replay

- work directly on `release-2025.4`
- copy the `docs-refactor` docs site content onto that branch
- keep this step isolated in its own commit

Exit criteria:

- Hugo tree, layout, styling, and navigation match `docs-refactor`
- no content rollback has been attempted yet

### Phase 2: Walk back `main`-only content

- process all `delete` items
- process all `revert` items
- process all `manual merge` items
- process all `restore` items

Exit criteria:

- site content reflects the `main`/`release-2025.4` split baseline
- Hugo structure remains intact

### Phase 3: Apply `release-2025.4` overlay

- update `compute/secrets.md` with the release-only delta
- confirm no other release-only deltas have appeared during validation

Exit criteria:

- content reflects the intended `release-2025.4` state on top of Hugo

### Phase 4: Validation

- validate page presence and absence against this manifest
- validate navigation entries
- validate cross-links and image paths
- validate admonitions and code blocks after content rollback
- validate local Hugo build

Exit criteria:

- build succeeds
- expected pages exist
- deleted pages are not surfaced
- intentionally omitted pages remain omitted

## Validation checklist

- [x] `infrastructure-argocd` remains omitted because it was not part of the
      surfaced navigation target
- [ ] Designate pages added on `main` are removed from the `release-2025.4`
      Hugo result
- [ ] Trove pages added on `main` are removed from the `release-2025.4` Hugo
      result
- [ ] external Ceph operator pages added on `main` are removed from the
      `release-2025.4` Hugo result
- [ ] `openstack-compute-kit-secrets` reflects the `release-2025.4` secret
      naming and additional password secrets
- [ ] the site still builds after the content rollback

## Decision log

### Open decisions

- exact Hugo destination for restored ArgoCD content
- whether any post-split `main` docs should intentionally remain in
  `release-2025.4` despite not being part of the strict rollback target
- whether additional `release-2025.4`-only deltas exist outside the already
  reviewed docs paths

### Confirmed decisions

- use `docs-refactor` as the structural base
- perform the work on `release-2025.4`
- roll content back to the `main` / `release-2025.4` split baseline
- overlay `release-2025.4` content after the rollback

## Progress log

- 2026-04-20: initial plan created from current local branch analysis
- 2026-04-20: pure `docs-refactor` structural transplant applied onto
  `release-2025.4` working tree; content rollback and release overlay still
  pending
- 2026-04-20: completed the first rollback pass for `delete` items from the
  `main`-only content set
- 2026-04-20: completed a first pass of direct `revert` items where the
  `main`-side delta mapped cleanly into the Hugo targets
- 2026-04-20: completed the mapped rollback work for OVN and the smaller
  section-index/manual-merge pages
- 2026-04-20: applied the known `release-2025.4` overlay to the compute
  secrets page
