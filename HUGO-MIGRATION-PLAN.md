# Hugo Migration Plan

Last updated: 2026-04-21

## Goal

Move `release-2026.1-rc` from MkDocs to Hugo while preserving `release-2026.1-rc`
documentation content except where a change is required to make the content render
correctly in Hugo.

## Current Branch

- Branch: `codex/release-2026.1-rc-hugo`
- Base: `release-2026.1-rc`
- Worktree: `/Users/ken/Dev/genestack`

## Pivot Decision

This branch does not continue the earlier hand-import work. It reuses the already
completed `release-2025.4` Hugo migration as the migration base, then preserves the
newer `release-2026.1-rc` MkDocs content that still needs to be ported.

That keeps the migration reversible:

- the Hugo platform import comes from known prior work
- the newer `release-2026.1-rc` page bodies are still present on this branch
- the remaining work is an explicit content-port backlog instead of implicit merge
  fallout

## Applied Migration Commits

These commits were cherry-picked from `release-2025.4`:

1. `4833c05d` `docs: update local tooling and pdf pipeline`
2. `a9e24425` `Migrate documentation from mkdocs to hugo`
3. `ac349d73` `PDF pipeline fix`
4. `4a563f80` `Fix Hugo build container`

## Post-Cherry-Pick Mechanical Fixes

These are release-branch path repairs, not intended content changes:

- [docs/content/deployment-guide/open-infrastructure/infrastructure/loki.md](/Users/ken/Dev/genestack-r26.1-hugo/docs/content/deployment-guide/open-infrastructure/infrastructure/loki.md)
  now references the `release-2026.1-rc` Loki example file names ending in
  `.yaml.example`
- [docs/content/deployment-guide/open-infrastructure/observability/exporters/openstack/_index.md](/Users/ken/Dev/genestack-r26.1-hugo/docs/content/deployment-guide/open-infrastructure/observability/exporters/openstack/_index.md)
  now references `base-helm-configs/openstack-metrics-exporter/clouds-yaml`

## Verified State

- `make -C docs build` succeeds on this branch
- the Hugo shell, layouts, assets, containers, PDF pipeline, and migrated content
  tree from `release-2025.4` are present
- newer `release-2026.1-rc` MkDocs pages that were not safely replaced during the
  transplant remain in the top-level `docs/` tree for follow-up porting

## Remaining Content Port Backlog

There are `45` top-level MkDocs content pages still present and acting as the source
of truth for `release-2026.1-rc` content that has not yet been ported into the Hugo
tree:

- `docs/etcd-backup.md`
- `docs/infrastructure-cert-manager.md`
- `docs/infrastructure-mariadb.md`
- `docs/infrastructure-memcached.md`
- `docs/k8s-labels.md`
- `docs/masakari-host-monitor.md`
- `docs/masakari-instance-introspec.md`
- `docs/monitoring-getting-started.md`
- `docs/monitoring-grafana.md`
- `docs/monitoring-loki.md`
- `docs/monitoring-observability-overview.md`
- `docs/monitoring-opentelemetry.md`
- `docs/monitoring-otel-base-metrics.md`
- `docs/monitoring-prometheus.md`
- `docs/monitoring-tempo.md`
- `docs/openstack-barbican-exporter.md`
- `docs/openstack-barbican.md`
- `docs/openstack-blazar-reservation-splitter.md`
- `docs/openstack-blazar.md`
- `docs/openstack-ceilometer.md`
- `docs/openstack-cinder-ceph-store.md`
- `docs/openstack-cinder-lvmisci.md`
- `docs/openstack-cinder.md`
- `docs/openstack-compute-ceph-store.md`
- `docs/openstack-compute-kit-secrets.md`
- `docs/openstack-compute-kit.md`
- `docs/openstack-designate-exporter.md`
- `docs/openstack-designate-neutron.md`
- `docs/openstack-designate-prep.md`
- `docs/openstack-designate.md`
- `docs/openstack-freezer-backup-retention.md`
- `docs/openstack-freezer.md`
- `docs/openstack-glance-ceph-store.md`
- `docs/openstack-glance.md`
- `docs/openstack-keystone-federation.md`
- `docs/openstack-keystone-ldap.md`
- `docs/openstack-mariadb-operator-upgrade.md`
- `docs/openstack-nested-virtualization.md`
- `docs/openstack-skyline.md`
- `docs/openstack-trove-mysql-images.md`
- `docs/openstack-trove.md`
- `docs/prometheus-openstack-metrics-exporter.md`
- `docs/prometheus-pushgateway.md`
- `docs/release-2026.1.md`
- `docs/release-notes.md`

Two MkDocs control files are also still present and should be removed only after the
content port is complete:

- `.github/workflows/mkdocs.yaml`
- `mkdocs.yml`

## Next Steps

1. Use [HUGO-CONTENT-PORT-MAP.md](/Users/ken/Dev/genestack/HUGO-CONTENT-PORT-MAP.md)
   as the source-to-destination map for the `45` preserved MkDocs pages.
2. Port content from each top-level MkDocs file into the correct Hugo destination,
   preserving `release-2026.1-rc` wording and examples unless a Hugo rendering fix is
   required.
3. Delete each legacy MkDocs source page only after its Hugo destination has been
   updated and verified.
4. Remove `.github/workflows/mkdocs.yaml` and `mkdocs.yml` only after the last
   preserved MkDocs page has been ported.
5. Re-run `make -C docs build` after each tranche.

## Working Rule

For the rest of this migration, `release-2026.1-rc` content wins and the reused
`release-2025.4` Hugo migration provides structure, rendering, layout, and build
tooling.
