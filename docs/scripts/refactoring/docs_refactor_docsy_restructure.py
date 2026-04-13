#!/usr/bin/env python3

from __future__ import annotations

import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / "docs" / "content"


SECTION_INDEXES = {
    "deployment-guide/getting-started": {
        "title": "Getting Started",
        "weight": 10,
        "description": "Core deployment workflow and initial environment bring-up guidance.",
    },
    "deployment-guide/infrastructure": {
        "title": "Infrastructure",
        "weight": 20,
        "description": "Foundational infrastructure services and shared platform dependencies.",
    },
    "deployment-guide/kubernetes": {
        "title": "Kubernetes",
        "weight": 30,
        "description": "Cluster bring-up, node configuration, CNI, and supporting Kubernetes tooling.",
    },
    "deployment-guide/openstack": {
        "title": "OpenStack",
        "weight": 40,
        "description": "OpenStack service deployment workflows and service-specific integration steps.",
    },
    "deployment-guide/observability": {
        "title": "Observability",
        "weight": 50,
        "description": "Monitoring, alerting, metrics, exporters, and dashboards.",
    },
    "deployment-guide/storage": {
        "title": "Storage",
        "weight": 60,
        "description": "Storage backends and storage service deployment options.",
    },
    "deployment-guide/secrets": {
        "title": "Secrets and Key Management",
        "weight": 70,
        "description": "Secret management and secret delivery components.",
    },
    "operations-guide/lifecycle": {
        "title": "Lifecycle",
        "weight": 10,
        "description": "Upgrades, node changes, backups, and environment lifecycle tasks.",
    },
    "operations-guide/platform": {
        "title": "Platform Operations",
        "weight": 20,
        "description": "Core Genestack operational guidance that is not tied to a single subsystem.",
    },
    "operations-guide/observability": {
        "title": "Observability",
        "weight": 30,
        "description": "Alerting, logging, dashboards, monitoring practices, and telemetry operations.",
    },
    "operations-guide/ovn": {
        "title": "OVN and Kube-OVN",
        "weight": 40,
        "description": "OVN networking operations, troubleshooting, and Kube-OVN procedures.",
    },
    "operations-guide/openstack": {
        "title": "OpenStack",
        "weight": 50,
        "description": "OpenStack administration, troubleshooting, quotas, storage, and service operations.",
    },
    "operations-guide/data-services": {
        "title": "Data Services",
        "weight": 60,
        "description": "MariaDB and related data-service operational procedures.",
    },
    "operations-guide/kubernetes": {
        "title": "Kubernetes",
        "weight": 70,
        "description": "Operational procedures tied directly to Kubernetes cluster management.",
    },
}


MOVE_MAP = {
    "deployment-guide/build-test-envs.md": "deployment-guide/getting-started/build-test-envs.md",
    "deployment-guide/genestack-getting-started.md": "deployment-guide/getting-started/genestack-getting-started.md",
    "deployment-guide/infrastructure-cert-manager.md": "deployment-guide/infrastructure/cert-manager.md",
    "deployment-guide/infrastructure-envoy-gateway-api-security.md": "deployment-guide/infrastructure/envoy-gateway-api-security.md",
    "deployment-guide/infrastructure-envoy-gateway-api.md": "deployment-guide/infrastructure/envoy-gateway-api.md",
    "deployment-guide/infrastructure-fluentbit.md": "deployment-guide/infrastructure/fluentbit.md",
    "deployment-guide/infrastructure-gateway-api.md": "deployment-guide/infrastructure/gateway-api.md",
    "deployment-guide/infrastructure-libvirt.md": "deployment-guide/infrastructure/libvirt.md",
    "deployment-guide/infrastructure-loki.md": "deployment-guide/infrastructure/loki.md",
    "deployment-guide/infrastructure-mariadb.md": "deployment-guide/infrastructure/mariadb.md",
    "deployment-guide/infrastructure-memcached.md": "deployment-guide/infrastructure/memcached.md",
    "deployment-guide/infrastructure-metallb.md": "deployment-guide/infrastructure/metallb.md",
    "deployment-guide/infrastructure-namespace.md": "deployment-guide/infrastructure/namespace.md",
    "deployment-guide/infrastructure-overview.md": "deployment-guide/infrastructure/overview.md",
    "deployment-guide/infrastructure-ovn-setup.md": "deployment-guide/infrastructure/ovn-setup.md",
    "deployment-guide/infrastructure-postgresql.md": "deployment-guide/infrastructure/postgresql.md",
    "deployment-guide/infrastructure-rabbitmq.md": "deployment-guide/infrastructure/rabbitmq.md",
    "deployment-guide/infrastructure-redis.md": "deployment-guide/infrastructure/redis.md",
    "deployment-guide/infrastructure-sealed-secrets.md": "deployment-guide/infrastructure/sealed-secrets.md",
    "deployment-guide/k8s-cni-kube-ovn.md": "deployment-guide/kubernetes/cni-kube-ovn.md",
    "deployment-guide/k8s-config.md": "deployment-guide/kubernetes/config.md",
    "deployment-guide/k8s-dashboard.md": "deployment-guide/kubernetes/dashboard.md",
    "deployment-guide/k8s-kubespray.md": "deployment-guide/kubernetes/kubespray.md",
    "deployment-guide/k8s-labels.md": "deployment-guide/kubernetes/labels.md",
    "deployment-guide/k8s-overview.md": "deployment-guide/kubernetes/overview.md",
    "deployment-guide/k8s-taint.md": "deployment-guide/kubernetes/taint.md",
    "deployment-guide/k8s-talos.md": "deployment-guide/kubernetes/talos.md",
    "deployment-guide/k8s-tools.md": "deployment-guide/kubernetes/tools.md",
    "deployment-guide/openstack-barbican-exporter.md": "deployment-guide/openstack/barbican-exporter.md",
    "deployment-guide/openstack-barbican.md": "deployment-guide/openstack/barbican.md",
    "deployment-guide/openstack-blazar.md": "deployment-guide/openstack/blazar.md",
    "deployment-guide/openstack-ceilometer.md": "deployment-guide/openstack/ceilometer.md",
    "deployment-guide/openstack-cinder-fips-encryption.md": "deployment-guide/openstack/cinder-fips-encryption.md",
    "deployment-guide/openstack-cinder-lvmisci.md": "deployment-guide/openstack/cinder-lvmiscsi.md",
    "deployment-guide/openstack-cinder-netapp-container.md": "deployment-guide/openstack/cinder-netapp-container.md",
    "deployment-guide/openstack-cinder-netapp-worker.md": "deployment-guide/openstack/cinder-netapp-worker.md",
    "deployment-guide/openstack-cinder.md": "deployment-guide/openstack/cinder.md",
    "deployment-guide/openstack-cloudkitty.md": "deployment-guide/openstack/cloudkitty.md",
    "deployment-guide/openstack-compute-kit-neutron.md": "deployment-guide/openstack/compute-kit-neutron.md",
    "deployment-guide/openstack-compute-kit-nova.md": "deployment-guide/openstack/compute-kit-nova.md",
    "deployment-guide/openstack-compute-kit-placement.md": "deployment-guide/openstack/compute-kit-placement.md",
    "deployment-guide/openstack-compute-kit-secrets.md": "deployment-guide/openstack/compute-kit-secrets.md",
    "deployment-guide/openstack-compute-kit.md": "deployment-guide/openstack/compute-kit.md",
    "deployment-guide/openstack-designate-exporter.md": "deployment-guide/openstack/designate-exporter.md",
    "deployment-guide/openstack-designate-neutron.md": "deployment-guide/openstack/designate-neutron.md",
    "deployment-guide/openstack-designate-prep.md": "deployment-guide/openstack/designate-prep.md",
    "deployment-guide/openstack-designate.md": "deployment-guide/openstack/designate.md",
    "deployment-guide/openstack-freezer.md": "deployment-guide/openstack/freezer.md",
    "deployment-guide/openstack-glance.md": "deployment-guide/openstack/glance.md",
    "deployment-guide/openstack-gnocchi.md": "deployment-guide/openstack/gnocchi.md",
    "deployment-guide/openstack-heat.md": "deployment-guide/openstack/heat.md",
    "deployment-guide/openstack-horizon.md": "deployment-guide/openstack/horizon.md",
    "deployment-guide/openstack-keystone.md": "deployment-guide/openstack/keystone.md",
    "deployment-guide/openstack-magnum.md": "deployment-guide/openstack/magnum.md",
    "deployment-guide/openstack-manila.md": "deployment-guide/openstack/manila.md",
    "deployment-guide/openstack-masakari.md": "deployment-guide/openstack/masakari.md",
    "deployment-guide/openstack-octavia.md": "deployment-guide/openstack/octavia.md",
    "deployment-guide/openstack-overview.md": "deployment-guide/openstack/overview.md",
    "deployment-guide/openstack-skyline.md": "deployment-guide/openstack/skyline.md",
    "deployment-guide/openstack-trove-mysql-images.md": "deployment-guide/openstack/trove-mysql-images.md",
    "deployment-guide/openstack-trove.md": "deployment-guide/openstack/trove.md",
    "deployment-guide/openstack-zaqar.md": "deployment-guide/openstack/zaqar.md",
    "deployment-guide/alertmanager-msteams.md": "deployment-guide/observability/alertmanager-msteams.md",
    "deployment-guide/alertmanager-pagerduty.md": "deployment-guide/observability/alertmanager-pagerduty.md",
    "deployment-guide/alertmanager-slack.md": "deployment-guide/observability/alertmanager-slack.md",
    "deployment-guide/grafana.md": "deployment-guide/observability/grafana.md",
    "deployment-guide/monitoring-getting-started.md": "deployment-guide/observability/getting-started.md",
    "deployment-guide/prometheus-blackbox-exporter.md": "deployment-guide/observability/prometheus-blackbox-exporter.md",
    "deployment-guide/prometheus-custom-node-metrics.md": "deployment-guide/observability/prometheus-custom-node-metrics.md",
    "deployment-guide/prometheus-kube-event-exporter.md": "deployment-guide/observability/prometheus-kube-event-exporter.md",
    "deployment-guide/prometheus-kube-ovn.md": "deployment-guide/observability/prometheus-kube-ovn.md",
    "deployment-guide/prometheus-memcached-exporter.md": "deployment-guide/observability/prometheus-memcached-exporter.md",
    "deployment-guide/prometheus-monitoring-overview.md": "deployment-guide/observability/prometheus-monitoring-overview.md",
    "deployment-guide/prometheus-mysql-exporter.md": "deployment-guide/observability/prometheus-mysql-exporter.md",
    "deployment-guide/prometheus-openstack-metrics-exporter.md": "deployment-guide/observability/prometheus-openstack-metrics-exporter.md",
    "deployment-guide/prometheus-postgres-exporter.md": "deployment-guide/observability/prometheus-postgres-exporter.md",
    "deployment-guide/prometheus-pushgateway.md": "deployment-guide/observability/prometheus-pushgateway.md",
    "deployment-guide/prometheus-rabbitmq-exporter.md": "deployment-guide/observability/prometheus-rabbitmq-exporter.md",
    "deployment-guide/prometheus-snmp-exporter.md": "deployment-guide/observability/prometheus-snmp-exporter.md",
    "deployment-guide/prometheus.md": "deployment-guide/observability/prometheus.md",
    "deployment-guide/storage-ceph-rook-external.md": "deployment-guide/storage/ceph-rook-external.md",
    "deployment-guide/storage-ceph-rook-internal.md": "deployment-guide/storage/ceph-rook-internal.md",
    "deployment-guide/storage-external-block.md": "deployment-guide/storage/external-block.md",
    "deployment-guide/storage-longhorn.md": "deployment-guide/storage/longhorn.md",
    "deployment-guide/storage-nfs-external.md": "deployment-guide/storage/nfs-external.md",
    "deployment-guide/storage-overview.md": "deployment-guide/storage/overview.md",
    "deployment-guide/storage-topolvm.md": "deployment-guide/storage/topolvm.md",
    "deployment-guide/sealed-secrets.md": "deployment-guide/secrets/sealed-secrets.md",
    "deployment-guide/vault-secrets-operator.md": "deployment-guide/secrets/vault-secrets-operator.md",
    "deployment-guide/vault.md": "deployment-guide/secrets/vault.md",
    "operations-guide/2024.1-to-2025.1.md": "operations-guide/lifecycle/2024.1-to-2025.1.md",
    "operations-guide/adding-new-node.md": "operations-guide/lifecycle/adding-new-node.md",
    "operations-guide/etcd-backup.md": "operations-guide/lifecycle/etcd-backup.md",
    "operations-guide/genestack-upgrade.md": "operations-guide/lifecycle/genestack-upgrade.md",
    "operations-guide/multi-region-support.md": "operations-guide/lifecycle/multi-region-support.md",
    "operations-guide/sync-fernet-keys.md": "operations-guide/lifecycle/sync-fernet-keys.md",
    "operations-guide/genestack-structure-and-files.md": "operations-guide/platform/genestack-structure-and-files.md",
    "operations-guide/alerting-info.md": "operations-guide/observability/alerting-info.md",
    "operations-guide/genestack-alerts.md": "operations-guide/observability/genestack-alerts.md",
    "operations-guide/genestack-logging.md": "operations-guide/observability/genestack-logging.md",
    "operations-guide/import-grafana-dashboard.md": "operations-guide/observability/import-grafana-dashboard.md",
    "operations-guide/metering-billing.md": "operations-guide/observability/metering-billing.md",
    "operations-guide/metering-ceilometer.md": "operations-guide/observability/metering-ceilometer.md",
    "operations-guide/metering-chargebacks.md": "operations-guide/observability/metering-chargebacks.md",
    "operations-guide/metering-gnocchi.md": "operations-guide/observability/metering-gnocchi.md",
    "operations-guide/metering-overview.md": "operations-guide/observability/metering-overview.md",
    "operations-guide/monitoring-info.md": "operations-guide/observability/monitoring-info.md",
    "operations-guide/observability-info.md": "operations-guide/observability/observability-info.md",
    "operations-guide/openstack-exporter.md": "operations-guide/observability/openstack-exporter.md",
    "operations-guide/prometheus-envoy-gateway.md": "operations-guide/observability/prometheus-envoy-gateway.md",
    "operations-guide/infrastructure-kube-ovn-re-ip.md": "operations-guide/ovn/infrastructure-kube-ovn-re-ip.md",
    "operations-guide/infrastructure-ovn-db-backup.md": "operations-guide/ovn/infrastructure-ovn-db-backup.md",
    "operations-guide/k8s-cni-kube-ovn-helm-conversion.md": "operations-guide/ovn/k8s-cni-kube-ovn-helm-conversion.md",
    "operations-guide/ovn-alert-claim-storm.md": "operations-guide/ovn/alert-claim-storm.md",
    "operations-guide/ovn-intro.md": "operations-guide/ovn/intro.md",
    "operations-guide/ovn-kube-ovn-openstack.md": "operations-guide/ovn/kube-ovn-openstack.md",
    "operations-guide/ovn-monitoring-introduction.md": "operations-guide/ovn/monitoring-introduction.md",
    "operations-guide/ovn-traffic-flow-intro.md": "operations-guide/ovn/traffic-flow-intro.md",
    "operations-guide/ovn-troubleshooting.md": "operations-guide/ovn/troubleshooting.md",
    "operations-guide/magnum-kubernetes-cluster-setup-guide.md": "operations-guide/openstack/magnum-kubernetes-cluster-setup-guide.md",
    "operations-guide/octavia-flavor-and-flavorprofile-guide.md": "operations-guide/openstack/octavia-flavor-and-flavorprofile-guide.md",
    "operations-guide/octavia-loadbalancer-setup-guide.md": "operations-guide/openstack/octavia-loadbalancer-setup-guide.md",
    "operations-guide/openstack-blazar-reservation-splitter.md": "operations-guide/openstack/blazar-reservation-splitter.md",
    "operations-guide/openstack-cinder-block-node-decommission-process.md": "operations-guide/openstack/cinder-block-node-decommission-process.md",
    "operations-guide/openstack-cinder-ceph-store.md": "operations-guide/openstack/cinder-ceph-store.md",
    "operations-guide/openstack-cinder-volume-provisioning-specs.md": "operations-guide/openstack/cinder-volume-provisioning-specs.md",
    "operations-guide/openstack-cinder-volume-qos-policies.md": "operations-guide/openstack/cinder-volume-qos-policies.md",
    "operations-guide/openstack-cinder-volume-type-specs.md": "operations-guide/openstack/cinder-volume-type-specs.md",
    "operations-guide/openstack-clouds.md": "operations-guide/openstack/clouds.md",
    "operations-guide/openstack-compute-ceph-store.md": "operations-guide/openstack/compute-ceph-store.md",
    "operations-guide/openstack-cpu-allocation-ratio.md": "operations-guide/openstack/cpu-allocation-ratio.md",
    "operations-guide/openstack-data-disk-recovery.md": "operations-guide/openstack/data-disk-recovery.md",
    "operations-guide/openstack-flavors.md": "operations-guide/openstack/flavors.md",
    "operations-guide/openstack-glance-ceph-store.md": "operations-guide/openstack/glance-ceph-store.md",
    "operations-guide/openstack-glance-images.md": "operations-guide/openstack/glance-images.md",
    "operations-guide/openstack-glance-swift-store.md": "operations-guide/openstack/glance-swift-store.md",
    "operations-guide/openstack-host-aggregates.md": "operations-guide/openstack/host-aggregates.md",
    "operations-guide/openstack-keystone-federation.md": "operations-guide/openstack/keystone-federation.md",
    "operations-guide/openstack-keystone-ldap.md": "operations-guide/openstack/keystone-ldap.md",
    "operations-guide/openstack-keystone-readonly.md": "operations-guide/openstack/keystone-readonly.md",
    "operations-guide/openstack-neutron-networks.md": "operations-guide/openstack/neutron-networks.md",
    "operations-guide/openstack-override-public-endpoint-fqdn.md": "operations-guide/openstack/override-public-endpoint-fqdn.md",
    "operations-guide/openstack-pci-passthrough.md": "operations-guide/openstack/pci-passthrough.md",
    "operations-guide/openstack-quota-managment.md": "operations-guide/openstack/quota-managment.md",
    "operations-guide/openstack-resource-lookups.md": "operations-guide/openstack/resource-lookups.md",
    "operations-guide/openstack-service-overrides.md": "operations-guide/openstack/service-overrides.md",
    "operations-guide/openstack-swift-operators-guide.md": "operations-guide/openstack/swift-operators-guide.md",
    "operations-guide/openstack-vendordata.md": "operations-guide/openstack/vendordata.md",
    "operations-guide/infrastructure-mariadb-ops.md": "operations-guide/data-services/infrastructure-mariadb-ops.md",
    "operations-guide/mariadb-backuprestore-from-tempauth.md": "operations-guide/data-services/mariadb-backuprestore-from-tempauth.md",
    "operations-guide/k8s-kubespray-upgrade.md": "operations-guide/kubernetes/kubespray-upgrade.md",
}


def rel_permalink(path: str) -> str:
    return "/" + path.removesuffix(".md").replace("_index", "").rstrip("/") + "/"


def ensure_alias(front_matter: str, alias: str) -> str:
    if alias in front_matter:
        return front_matter
    if re.search(r"^aliases:\s*$", front_matter, flags=re.MULTILINE):
        return re.sub(r"(^aliases:\s*$\n)", rf"\1  - {alias}\n", front_matter, count=1, flags=re.MULTILINE)
    closing = front_matter.rfind("---\n")
    if closing == -1:
        return front_matter
    return front_matter[:closing] + f"aliases:\n  - {alias}\n" + front_matter[closing:]


def move_page(old_rel: str, new_rel: str) -> None:
    old_path = DOCS / old_rel
    new_path = DOCS / new_rel
    if not old_path.exists():
        return
    new_path.parent.mkdir(parents=True, exist_ok=True)
    text = old_path.read_text()
    if text.startswith("---\n"):
        parts = re.split(r"^---\s*$\n", text, maxsplit=2, flags=re.MULTILINE)
        if len(parts) == 3 and parts[0] == "":
            front_matter = f"---\n{parts[1]}---\n"
            body = parts[2]
            front_matter = ensure_alias(front_matter, rel_permalink(old_rel))
            text = front_matter + body
    new_path.write_text(text)
    old_path.unlink()


def write_index(relative_dir: str, title: str, weight: int, description: str) -> None:
    target = DOCS / relative_dir / "_index.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "---\n"
        f'title: "{title}"\n'
        f"weight: {weight}\n"
        "type: docs\n"
        "simple_list: true\n"
        f'description: "{description}"\n'
        "cascade:\n"
        "  - type: docs\n"
        "---\n\n"
        f"{description}\n"
    )


def main() -> None:
    for relative_dir, meta in SECTION_INDEXES.items():
        write_index(relative_dir, meta["title"], meta["weight"], meta["description"])
    for old_rel, new_rel in MOVE_MAP.items():
        move_page(old_rel, new_rel)


if __name__ == "__main__":
    main()
