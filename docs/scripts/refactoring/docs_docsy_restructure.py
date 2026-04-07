#!/usr/bin/env python3

from __future__ import annotations

import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
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
    "operational-guide/lifecycle": {
        "title": "Lifecycle",
        "weight": 10,
        "description": "Upgrades, node changes, backups, and environment lifecycle tasks.",
    },
    "operational-guide/platform": {
        "title": "Platform Operations",
        "weight": 20,
        "description": "Core Genestack operational guidance that is not tied to a single subsystem.",
    },
    "operational-guide/observability": {
        "title": "Observability",
        "weight": 30,
        "description": "Alerting, logging, dashboards, monitoring practices, and telemetry operations.",
    },
    "operational-guide/ovn": {
        "title": "OVN and Kube-OVN",
        "weight": 40,
        "description": "OVN networking operations, troubleshooting, and Kube-OVN procedures.",
    },
    "operational-guide/openstack": {
        "title": "OpenStack",
        "weight": 50,
        "description": "OpenStack administration, troubleshooting, quotas, storage, and service operations.",
    },
    "operational-guide/data-services": {
        "title": "Data Services",
        "weight": 60,
        "description": "MariaDB and related data-service operational procedures.",
    },
    "operational-guide/kubernetes": {
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
    "operational-guide/2024.1-to-2025.1.md": "operational-guide/lifecycle/2024.1-to-2025.1.md",
    "operational-guide/adding-new-node.md": "operational-guide/lifecycle/adding-new-node.md",
    "operational-guide/etcd-backup.md": "operational-guide/lifecycle/etcd-backup.md",
    "operational-guide/genestack-upgrade.md": "operational-guide/lifecycle/genestack-upgrade.md",
    "operational-guide/multi-region-support.md": "operational-guide/lifecycle/multi-region-support.md",
    "operational-guide/sync-fernet-keys.md": "operational-guide/lifecycle/sync-fernet-keys.md",
    "operational-guide/genestack-structure-and-files.md": "operational-guide/platform/genestack-structure-and-files.md",
    "operational-guide/alerting-info.md": "operational-guide/observability/alerting-info.md",
    "operational-guide/genestack-alerts.md": "operational-guide/observability/genestack-alerts.md",
    "operational-guide/genestack-logging.md": "operational-guide/observability/genestack-logging.md",
    "operational-guide/import-grafana-dashboard.md": "operational-guide/observability/import-grafana-dashboard.md",
    "operational-guide/metering-billing.md": "operational-guide/observability/metering-billing.md",
    "operational-guide/metering-ceilometer.md": "operational-guide/observability/metering-ceilometer.md",
    "operational-guide/metering-chargebacks.md": "operational-guide/observability/metering-chargebacks.md",
    "operational-guide/metering-gnocchi.md": "operational-guide/observability/metering-gnocchi.md",
    "operational-guide/metering-overview.md": "operational-guide/observability/metering-overview.md",
    "operational-guide/monitoring-info.md": "operational-guide/observability/monitoring-info.md",
    "operational-guide/observability-info.md": "operational-guide/observability/observability-info.md",
    "operational-guide/openstack-exporter.md": "operational-guide/observability/openstack-exporter.md",
    "operational-guide/prometheus-envoy-gateway.md": "operational-guide/observability/prometheus-envoy-gateway.md",
    "operational-guide/infrastructure-kube-ovn-re-ip.md": "operational-guide/ovn/infrastructure-kube-ovn-re-ip.md",
    "operational-guide/infrastructure-ovn-db-backup.md": "operational-guide/ovn/infrastructure-ovn-db-backup.md",
    "operational-guide/k8s-cni-kube-ovn-helm-conversion.md": "operational-guide/ovn/k8s-cni-kube-ovn-helm-conversion.md",
    "operational-guide/ovn-alert-claim-storm.md": "operational-guide/ovn/alert-claim-storm.md",
    "operational-guide/ovn-intro.md": "operational-guide/ovn/intro.md",
    "operational-guide/ovn-kube-ovn-openstack.md": "operational-guide/ovn/kube-ovn-openstack.md",
    "operational-guide/ovn-monitoring-introduction.md": "operational-guide/ovn/monitoring-introduction.md",
    "operational-guide/ovn-traffic-flow-intro.md": "operational-guide/ovn/traffic-flow-intro.md",
    "operational-guide/ovn-troubleshooting.md": "operational-guide/ovn/troubleshooting.md",
    "operational-guide/magnum-kubernetes-cluster-setup-guide.md": "operational-guide/openstack/magnum-kubernetes-cluster-setup-guide.md",
    "operational-guide/octavia-flavor-and-flavorprofile-guide.md": "operational-guide/openstack/octavia-flavor-and-flavorprofile-guide.md",
    "operational-guide/octavia-loadbalancer-setup-guide.md": "operational-guide/openstack/octavia-loadbalancer-setup-guide.md",
    "operational-guide/openstack-blazar-reservation-splitter.md": "operational-guide/openstack/blazar-reservation-splitter.md",
    "operational-guide/openstack-cinder-block-node-decommission-process.md": "operational-guide/openstack/cinder-block-node-decommission-process.md",
    "operational-guide/openstack-cinder-ceph-store.md": "operational-guide/openstack/cinder-ceph-store.md",
    "operational-guide/openstack-cinder-volume-provisioning-specs.md": "operational-guide/openstack/cinder-volume-provisioning-specs.md",
    "operational-guide/openstack-cinder-volume-qos-policies.md": "operational-guide/openstack/cinder-volume-qos-policies.md",
    "operational-guide/openstack-cinder-volume-type-specs.md": "operational-guide/openstack/cinder-volume-type-specs.md",
    "operational-guide/openstack-clouds.md": "operational-guide/openstack/clouds.md",
    "operational-guide/openstack-compute-ceph-store.md": "operational-guide/openstack/compute-ceph-store.md",
    "operational-guide/openstack-cpu-allocation-ratio.md": "operational-guide/openstack/cpu-allocation-ratio.md",
    "operational-guide/openstack-data-disk-recovery.md": "operational-guide/openstack/data-disk-recovery.md",
    "operational-guide/openstack-flavors.md": "operational-guide/openstack/flavors.md",
    "operational-guide/openstack-glance-ceph-store.md": "operational-guide/openstack/glance-ceph-store.md",
    "operational-guide/openstack-glance-images.md": "operational-guide/openstack/glance-images.md",
    "operational-guide/openstack-glance-swift-store.md": "operational-guide/openstack/glance-swift-store.md",
    "operational-guide/openstack-host-aggregates.md": "operational-guide/openstack/host-aggregates.md",
    "operational-guide/openstack-keystone-federation.md": "operational-guide/openstack/keystone-federation.md",
    "operational-guide/openstack-keystone-ldap.md": "operational-guide/openstack/keystone-ldap.md",
    "operational-guide/openstack-keystone-readonly.md": "operational-guide/openstack/keystone-readonly.md",
    "operational-guide/openstack-neutron-networks.md": "operational-guide/openstack/neutron-networks.md",
    "operational-guide/openstack-override-public-endpoint-fqdn.md": "operational-guide/openstack/override-public-endpoint-fqdn.md",
    "operational-guide/openstack-pci-passthrough.md": "operational-guide/openstack/pci-passthrough.md",
    "operational-guide/openstack-quota-managment.md": "operational-guide/openstack/quota-managment.md",
    "operational-guide/openstack-resource-lookups.md": "operational-guide/openstack/resource-lookups.md",
    "operational-guide/openstack-service-overrides.md": "operational-guide/openstack/service-overrides.md",
    "operational-guide/openstack-swift-operators-guide.md": "operational-guide/openstack/swift-operators-guide.md",
    "operational-guide/openstack-vendordata.md": "operational-guide/openstack/vendordata.md",
    "operational-guide/infrastructure-mariadb-ops.md": "operational-guide/data-services/infrastructure-mariadb-ops.md",
    "operational-guide/mariadb-backuprestore-from-tempauth.md": "operational-guide/data-services/mariadb-backuprestore-from-tempauth.md",
    "operational-guide/k8s-kubespray-upgrade.md": "operational-guide/kubernetes/kubespray-upgrade.md",
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
