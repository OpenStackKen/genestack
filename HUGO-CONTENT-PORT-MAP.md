# Hugo Content Port Map

Last updated: 2026-04-21

## Scope

This map covers the `45` top-level MkDocs content pages that changed between
`upstream/release-2025.4` and `release-2026.1-rc`.

The goal is not to prove exact semantic equivalence for every page. The goal is
to decide which source to trust while porting each page into the Hugo tree on
`codex/release-2026.1-rc-hugo`.

## Completed Safe Tranche

The following pages have already been imported into the current branch from
`docs-refactor`, verified with `make -C docs build`, and had their legacy
top-level MkDocs source pages removed:

- `docs/infrastructure-cert-manager.md`
- `docs/openstack-barbican-exporter.md`
- `docs/openstack-blazar-reservation-splitter.md`
- `docs/openstack-cinder-ceph-store.md`
- `docs/openstack-compute-ceph-store.md`
- `docs/openstack-designate-exporter.md`
- `docs/openstack-designate-neutron.md`
- `docs/openstack-designate-prep.md`
- `docs/openstack-designate.md`
- `docs/openstack-glance-ceph-store.md`
- `docs/openstack-keystone-ldap.md`
- `docs/openstack-trove-mysql-images.md`
- `docs/openstack-trove.md`

## Rules

- `Safe to take from docs-refactor` means `docs-refactor` already contains a
  Hugo page that is close enough to the `release-2026.1-rc` MkDocs content that
  it can be used as the starting point without first re-porting the MkDocs body.
- `Use docs-refactor structure, port 2026.1 content` means the Hugo destination
  exists or the section placement is clear, but the body on `docs-refactor` is
  older, only partial, or otherwise not trustworthy as the final content source.
- `Port from MkDocs directly` means `docs-refactor` has no meaningful Hugo page
  for the topic. The destination shown here is a proposed path when no existing
  Hugo file is available.

## Safe To Take From `docs-refactor`

| MkDocs source | Hugo destination | Basis |
| --- | --- | --- |
| `docs/infrastructure-cert-manager.md` | `docs/content/deployment-guide/open-infrastructure/infrastructure/cert-manager.md` | New `2026.1` topic is already present as a dedicated Hugo page. |
| `docs/openstack-barbican-exporter.md` | `docs/content/deployment-guide/open-infrastructure/observability/exporters/openstack/barbican.md` | Direct exporter page already exists and closely matches the MkDocs source. |
| `docs/openstack-blazar-reservation-splitter.md` | `docs/content/operations-guide/openstack/blazar.md` | The reservation-splitter content is already folded into the Hugo Blazar ops page. |
| `docs/openstack-cinder-ceph-store.md` | `docs/content/operations-guide/openstack/cinder/cinder-ceph-store.md` | Dedicated Hugo page already exists and matches the new Ceph-store content. |
| `docs/openstack-compute-ceph-store.md` | `docs/content/operations-guide/openstack/nova/nova-external-ceph.md` | The external Ceph compute guidance is already represented in the Hugo Nova ops page. |
| `docs/openstack-designate-exporter.md` | `docs/content/deployment-guide/open-infrastructure/observability/exporters/openstack/designate.md` | Designate exporter content already exists on `docs-refactor`; this file is not yet on the current branch but the path is present on `docs-refactor`. |
| `docs/openstack-designate-neutron.md` | `docs/content/deployment-guide/open-infrastructure/openstack/designate/neutron.md` | Dedicated Hugo page already exists and tracks the MkDocs source closely. |
| `docs/openstack-designate-prep.md` | `docs/content/deployment-guide/open-infrastructure/openstack/designate/prepare.md` | Dedicated Hugo page already exists and tracks the MkDocs source closely. |
| `docs/openstack-designate.md` | `docs/content/deployment-guide/open-infrastructure/openstack/designate/deploy.md` | The deployment topic already exists as a dedicated Hugo page on `docs-refactor`. |
| `docs/openstack-glance-ceph-store.md` | `docs/content/operations-guide/openstack/glance/ceph-storage.md` | Dedicated Hugo page already exists and matches the new Glance Ceph content. |
| `docs/openstack-keystone-ldap.md` | `docs/content/operations-guide/openstack/keystone/ldap.md` | Dedicated Hugo page already exists and matches the new LDAP content. |
| `docs/openstack-trove-mysql-images.md` | `docs/content/deployment-guide/open-infrastructure/openstack/trove/mysql.md` | The Trove MySQL page already contains the image guidance added in `2026.1`. |
| `docs/openstack-trove.md` | `docs/content/deployment-guide/open-infrastructure/openstack/trove/_index.md` | The Trove section index already carries the new top-level Trove content. |

## Use `docs-refactor` Structure, Port `release-2026.1-rc` Content

| MkDocs source | Hugo destination | Basis |
| --- | --- | --- |
| `docs/etcd-backup.md` | `docs/content/operations-guide/infrastructure/kubernetes/etcd-backup.md` | A destination exists and `docs-refactor` is close, but `release-2026.1-rc` wording should remain authoritative. |
| `docs/infrastructure-mariadb.md` | `docs/content/deployment-guide/open-infrastructure/infrastructure/mariadb.md` | Destination exists, but `docs-refactor` still looks closer to older `2025.4` content. |
| `docs/infrastructure-memcached.md` | `docs/content/deployment-guide/open-infrastructure/infrastructure/memcached.md` | Destination exists, but `docs-refactor` still looks closer to older `2025.4` content. |
| `docs/k8s-labels.md` | `docs/content/deployment-guide/open-infrastructure/kubernetes/post-deployment/labels.md` | Destination exists, but `docs-refactor` still looks older than the `2026.1` MkDocs page. |
| `docs/masakari-host-monitor.md` | `docs/content/deployment-guide/open-infrastructure/openstack/masakari/host-monitor.md` | `docs-refactor` only has the parent Masakari deployment page. Use that section placement, but create a new child page for the host-monitor content. |
| `docs/masakari-instance-introspec.md` | `docs/content/deployment-guide/open-infrastructure/openstack/masakari/instance-introspection.md` | `docs-refactor` only has the parent Masakari deployment page. Use that section placement, but create a new child page for the instance/introspection monitor content. |
| `docs/monitoring-getting-started.md` | `docs/content/deployment-guide/open-infrastructure/observability/getting-started.md` | `docs-refactor` has the observability section but no trustworthy page for the `2026.1` install-order guide. Create a child page under that section. |
| `docs/monitoring-grafana.md` | `docs/content/deployment-guide/open-infrastructure/observability/grafana.md` | Destination exists, but the `docs-refactor` body is only partial relative to the `2026.1` page. |
| `docs/monitoring-loki.md` | `docs/content/deployment-guide/open-infrastructure/infrastructure/loki.md` | Destination exists, but the `docs-refactor` body is only partial relative to the `2026.1` page. |
| `docs/monitoring-observability-overview.md` | `docs/content/deployment-guide/open-infrastructure/observability/_index.md` | `docs-refactor` already uses this section landing page for the observability overview, but the `2026.1` page is much more complete and should replace the section body. |
| `docs/monitoring-prometheus.md` | `docs/content/deployment-guide/open-infrastructure/observability/prometheus.md` | Destination exists, but the `docs-refactor` body is only partial relative to the `2026.1` page. |
| `docs/openstack-barbican.md` | `docs/content/deployment-guide/open-infrastructure/openstack/barbican/_index.md` | Destination exists and the content is related, but the branch comparison was mixed rather than clearly `2026.1`-aligned. |
| `docs/openstack-blazar.md` | `docs/content/deployment-guide/open-infrastructure/openstack/blazar.md` | Destination exists and is closer to `2026.1`, but the safer rule is still to port the `release-2026.1-rc` body explicitly. |
| `docs/openstack-ceilometer.md` | `docs/content/deployment-guide/open-infrastructure/openstack/metering/ceilometer.md` | Destination exists, but `docs-refactor` still looks older than the `2026.1` MkDocs page. |
| `docs/openstack-cinder.md` | `docs/content/deployment-guide/open-infrastructure/openstack/cinder/_index.md` | Destination exists, but the comparison was mixed; preserve the `2026.1` page body. |
| `docs/openstack-cinder-lvmisci.md` | `docs/content/deployment-guide/open-infrastructure/openstack/cinder/cinder-lvmiscsi.md` | Destination exists, but `docs-refactor` still looks older than the `2026.1` MkDocs page. |
| `docs/openstack-compute-kit.md` | `docs/content/deployment-guide/open-infrastructure/openstack/compute/_index.md` | Destination exists, but `docs-refactor` still looks older than the `2026.1` MkDocs page. |
| `docs/openstack-compute-kit-secrets.md` | `docs/content/deployment-guide/open-infrastructure/openstack/compute/secrets.md` | Destination exists, but the comparison was mixed rather than clearly `2026.1`-aligned. |
| `docs/openstack-freezer.md` | `docs/content/deployment-guide/open-infrastructure/openstack/freezer.md` | Destination exists, but `docs-refactor` still looks substantially older than the `2026.1` MkDocs page. |
| `docs/openstack-glance.md` | `docs/content/deployment-guide/open-infrastructure/openstack/glance.md` | Destination exists and is closer to `2026.1`, but the safer rule is still to port the `release-2026.1-rc` body explicitly. |
| `docs/openstack-keystone-federation.md` | `docs/content/operations-guide/openstack/keystone/federation.md` | Destination exists, but the comparison was mixed rather than clearly `2026.1`-aligned. |
| `docs/openstack-skyline.md` | `docs/content/deployment-guide/open-infrastructure/openstack/dashboards/skyline.md` | Destination exists, but `docs-refactor` still looks older than the `2026.1` MkDocs page. |
| `docs/prometheus-openstack-metrics-exporter.md` | `docs/content/deployment-guide/open-infrastructure/observability/exporters/openstack/_index.md` | This is a deployment-oriented page, so the exporter deployment index is the right Hugo destination. Keep the `2026.1` deployment workflow rather than trusting the `docs-refactor` body. |
| `docs/prometheus-pushgateway.md` | `docs/content/deployment-guide/open-infrastructure/observability/exporters/pushgateway.md` | Destination exists, but `docs-refactor` still looks older than the `2026.1` MkDocs page. |
| `docs/release-notes.md` | `docs/content/overview/release-notes.md` | `docs-refactor` only carries a generic release-notes page. Keep the `2026.1` index content and update links to the versioned Hugo release page. |

## Port From MkDocs Directly

| MkDocs source | Hugo destination | Basis |
| --- | --- | --- |
| `docs/monitoring-opentelemetry.md` | `docs/content/deployment-guide/open-infrastructure/observability/opentelemetry.md` | No meaningful `docs-refactor` page exists for this topic. This destination is proposed based on the existing observability section layout. |
| `docs/monitoring-otel-base-metrics.md` | `docs/content/operations-guide/observability/otel-base-metrics.md` | No meaningful `docs-refactor` page exists for this reference content. This destination is proposed as a new operations-guide reference page. |
| `docs/monitoring-tempo.md` | `docs/content/deployment-guide/open-infrastructure/observability/tempo.md` | No meaningful `docs-refactor` page exists for this topic. This destination is proposed based on the existing observability section layout. |
| `docs/openstack-freezer-backup-retention.md` | `docs/content/operations-guide/openstack/freezer/backup-retention.md` | No meaningful `docs-refactor` page exists for this runbook. This destination is proposed as a new Freezer operations page. |
| `docs/openstack-mariadb-operator-upgrade.md` | `docs/content/operations-guide/infrastructure/mariadb/operator-upgrade.md` | No meaningful `docs-refactor` page exists for this runbook. This destination is proposed under the existing MariaDB operations section. |
| `docs/openstack-nested-virtualization.md` | `docs/content/operations-guide/openstack/nova/nested-virtualization.md` | No meaningful `docs-refactor` page exists for this operator guidance. This destination is proposed under the existing Nova operations section. |
| `docs/release-2026.1.md` | `docs/content/overview/releases/2026.1.md` | No meaningful `docs-refactor` page exists for the versioned release body. This destination is proposed as a new versioned release page linked from `docs/content/overview/release-notes.md`. |

## Control Files

These are not content pages, but they should be handled after the content port is
complete:

| MkDocs source | Hugo action |
| --- | --- |
| `.github/workflows/mkdocs.yaml` | Remove after the last preserved top-level MkDocs page is ported. |
| `mkdocs.yml` | Remove after the last preserved top-level MkDocs page is ported. |
