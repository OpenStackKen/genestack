#!/usr/bin/env python3

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

SECTION_FILES = {
    "overview": [
        "genestack-architecture.md",
        "genestack-components.md",
        "openstack-object-storage-swift.md",
        "release-notes.md",
        "product-matrix.md",
    ],
    "design-guide": [
        "sdlc.md",
        "accelerated-computing-overview.md",
        "accelerated-computing-infrastructure.md",
        "openstack-cloud-design-topology.md",
        "openstack-cloud-design-regions.md",
        "openstack-cloud-design-az.md",
        "openstack-cloud-design-ha.md",
        "openstack-cloud-design-dr.md",
        "openstack-cloud-design-genestack-infra.md",
        "documentation-standards.md",
    ],
    "cloud-onboarding": [
        "openstack-deploy-cli.md",
        "openstack-getting-started-cli.md",
        "openstack-security-groups.md",
        "openstack-floating-ips.md",
        "openstack-keypairs.md",
        "openstack-servers.md",
        "openstack-router.md",
        "openstack-images.md",
        "openstack-metrics.md",
        "storage-object-store-openstack-cli.md",
        "storage-object-store-swift-cli.md",
        "storage-object-store-s3-cli.md",
        "storage-object-store-skyline-gui.md",
        "storage-object-store-swift-3rd-party.md",
        "openstack-snapshot.md",
        "openstack-volumes.md",
        "openstack-load-balancer.md",
        "openstack-networks.md",
        "openstack-quota.md",
    ],
    "security-primer": [
        "security-lifecycle.md",
        "security-stages.md",
        "security-summary.md",
    ],
    "regions": ["api-status.md"],
    "info": ["mkdocs-howto.md"],
    "operational-guide": [
        "genestack-structure-and-files.md",
        "multi-region-support.md",
        "sync-fernet-keys.md",
        "genestack-upgrade.md",
        "metering-overview.md",
        "metering-ceilometer.md",
        "metering-gnocchi.md",
        "metering-billing.md",
        "metering-chargebacks.md",
        "etcd-backup.md",
        "adding-new-node.md",
        "k8s-kubespray-upgrade.md",
        "ovn-intro.md",
        "ovn-troubleshooting.md",
        "ovn-traffic-flow-intro.md",
        "infrastructure-ovn-db-backup.md",
        "ovn-monitoring-introduction.md",
        "ovn-alert-claim-storm.md",
        "ovn-kube-ovn-openstack.md",
        "infrastructure-kube-ovn-re-ip.md",
        "k8s-cni-kube-ovn-helm-conversion.md",
        "infrastructure-mariadb-ops.md",
        "mariadb-backuprestore-from-tempauth.md",
        "observability-info.md",
        "monitoring-info.md",
        "alerting-info.md",
        "genestack-logging.md",
        "2024.1-to-2025.1.md",
        "openstack-clouds.md",
        "openstack-cinder-volume-provisioning-specs.md",
        "openstack-cinder-volume-qos-policies.md",
        "openstack-cinder-volume-type-specs.md",
        "openstack-cinder-block-node-decommission-process.md",
        "openstack-cinder-ceph-store.md",
        "openstack-flavors.md",
        "openstack-cpu-allocation-ratio.md",
        "openstack-pci-passthrough.md",
        "openstack-compute-ceph-store.md",
        "openstack-host-aggregates.md",
        "openstack-data-disk-recovery.md",
        "openstack-vendordata.md",
        "openstack-quota-managment.md",
        "openstack-glance-images.md",
        "openstack-glance-swift-store.md",
        "openstack-glance-ceph-store.md",
        "openstack-keystone-federation.md",
        "openstack-keystone-ldap.md",
        "openstack-keystone-readonly.md",
        "openstack-neutron-networks.md",
        "magnum-kubernetes-cluster-setup-guide.md",
        "octavia-flavor-and-flavorprofile-guide.md",
        "octavia-loadbalancer-setup-guide.md",
        "openstack-swift-operators-guide.md",
        "openstack-override-public-endpoint-fqdn.md",
        "openstack-service-overrides.md",
        "openstack-resource-lookups.md",
        "openstack-blazar-reservation-splitter.md",
        "openstack-exporter.md",
        "import-grafana-dashboard.md",
        "genestack-alerts.md",
        "prometheus-envoy-gateway.md",
    ],
}

SPECIAL_DESTINATIONS = {
    "index.md": "_index.md",
    "openstack-cloud-design-intro.md": "design-guide/_index.md",
    "deployment-guide-welcome.md": "deployment-guide/_index.md",
    "cloud-onboarding-welcome.md": "cloud-onboarding/_index.md",
    "security-introduction.md": "security-primer/_index.md",
    "mkdocs-howto.md": "info/local-docs.md",
}

ALERT_MAP = {
    "note": "NOTE",
    "info": "NOTE",
    "abstract": "NOTE",
    "example": "IMPORTANT",
    "genestack": "IMPORTANT",
    "banner": "IMPORTANT",
    "tip": "TIP",
    "success": "TIP",
    "warning": "WARNING",
    "caution": "CAUTION",
}


def humanize(name: str) -> str:
    parts = re.sub(r"\.md$", "", name).split("-")
    return " ".join(part if re.match(r"^\d", part) else part.capitalize() for part in parts)


def strip_leading_frontmatter(content: str) -> str:
    if not content.startswith("---\n"):
        return content
    parts = re.split(r"^---\s*$\n", content, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3 or parts[0] != "":
        return content
    return parts[2]


def extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return re.sub(r"^#\s+", "", stripped).strip()
    return fallback


def deindent(lines: list[str]) -> list[str]:
    output = []
    for line in lines:
        if line.startswith("    "):
            output.append(line[4:])
        elif line.startswith("\t"):
            output.append(line[1:])
        else:
            output.append(line)
    return output


def convert_admonitions(content: str) -> str:
    lines = content.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        match = re.match(r'^!!!\s+([A-Za-z]+)(?:\s+"([^"]+)")?\s*$', lines[i])
        if not match:
            out.append(lines[i])
            i += 1
            continue
        kind = ALERT_MAP.get(match.group(1).lower(), "NOTE")
        title = match.group(2)
        i += 1
        block: list[str] = []
        while i < len(lines):
            current = lines[i]
            if not (current.strip() == "" or current.startswith("    ") or current.startswith("\t")):
                break
            block.append(current)
            i += 1
        block = deindent(block)
        out.append(f"> [!{kind}]\n")
        if title:
            out.append(f"> **{title}**\n")
        if block:
            out.append(">\n")
        for entry in block:
            out.append(">\n" if entry.strip() == "" else f"> {entry}")
        if not out[-1].endswith("\n\n"):
            out.append("\n")
    return "".join(out)


def convert_tabs(content: str) -> str:
    lines = content.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        match = re.match(r'^===\s+"([^"]+)"\s*$', lines[i])
        if not match:
            out.append(lines[i])
            i += 1
            continue
        title = match.group(1)
        i += 1
        block: list[str] = []
        while i < len(lines):
            current = lines[i]
            if not (current.strip() == "" or current.startswith("    ") or current.startswith("\t")):
                break
            block.append(current)
            i += 1
        out.append(f"\n### {title}\n\n")
        out.extend(deindent(block))
        if not out[-1].endswith("\n\n"):
            out.append("\n")
    return "".join(out)


def cleanup_markup(content: str) -> str:
    content = re.sub(r"\{:[^}]+\}", "", content)
    content = re.sub(r"<br clear=\"left\">\n?", "", content, flags=re.IGNORECASE)
    content = re.sub(r"<meta http-equiv=\"refresh\" content=\"420\">\n?", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\]\((?:\./)?assets/", "](/assets/", content)
    content = re.sub(r"\((?:\./)?assets/", "(/assets/", content)
    content = re.sub(r"src=(['\"])(?:\./)?assets/", r"src=\1/assets/", content)
    return content


def permalink_for_destination(destination: str) -> str:
    if destination == "_index.md":
        return "/"
    if destination.endswith("/_index.md"):
        return f"/{re.sub(r'/_index\.md$', '/', destination)}"
    return f"/{re.sub(r'\.md$', '/', destination)}"


def rewrite_links(content: str, destination_map: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        raw = match.group(1)
        if re.match(r"^[a-z]+://", raw, flags=re.IGNORECASE):
            return f"({raw})"
        page, anchor = (raw.split("#", 1) + [None])[:2]
        target = destination_map.get(os.path.basename(page))
        if not target:
            return f"({raw})"
        href = permalink_for_destination(target)
        if anchor:
            href = f"{href}#{anchor}"
        return f"({href})"

    return re.sub(r"\(([^)]+?\.md(?:#[^)]+)?)\)", repl, content)


def build_destination_map(markdown_files: list[str]) -> dict[str, str]:
    seen: set[str] = set()
    for file_name in [entry for entries in SECTION_FILES.values() for entry in entries]:
        if file_name in seen:
            raise ValueError(f"Duplicate mapping for {file_name}")
        seen.add(file_name)
    section_lookup = {
        file_name: section
        for section, files in SECTION_FILES.items()
        for file_name in files
    }
    result: dict[str, str] = {}
    for file_name in markdown_files:
        if file_name.startswith("info/"):
            continue
        if file_name in SPECIAL_DESTINATIONS:
            destination = SPECIAL_DESTINATIONS[file_name]
        else:
            destination = f"{section_lookup.get(file_name, 'deployment-guide')}/{file_name}"
        result[file_name] = destination
    return result


def prepend_frontmatter(content: str, title: str, weight: int, aliases: list[str]) -> str:
    escaped_title = title.replace('"', '\\"')
    frontmatter = ["---", f'title: "{escaped_title}"', f"weight: {weight}"]
    if aliases:
        frontmatter.append("aliases:")
        frontmatter.extend(f"  - {alias}" for alias in aliases)
    frontmatter.append("---")
    return "\n".join(frontmatter) + "\n\n" + content.lstrip()


def main() -> None:
    markdown_files = sorted(path.name for path in DOCS.iterdir() if path.suffix == ".md")
    destination_map = build_destination_map(markdown_files)

    backup_dir = ROOT / ".docs-refactor-backup"
    shutil.rmtree(backup_dir, ignore_errors=True)
    backup_dir.mkdir(parents=True, exist_ok=True)
    for file_name in markdown_files:
        shutil.copy2(DOCS / file_name, backup_dir / file_name)

    section_weights: dict[str, int] = {}
    ordered = sorted(destination_map.items(), key=lambda item: (item[1].count("/"), item[1], item[0]))
    for source, destination in ordered:
        source_path = DOCS / source
        if not source_path.exists():
            continue
        content = source_path.read_text()
        content = strip_leading_frontmatter(content)
        title = extract_title(content, humanize(source_path.name))
        content = convert_tabs(content)
        content = convert_admonitions(content)
        content = cleanup_markup(content)
        content = rewrite_links(content, destination_map)

        section = "root" if destination == "_index.md" else destination.split("/", 1)[0]
        section_weights[section] = section_weights.get(section, 0) + 10
        aliases = [f"/{source_path.stem}/"]
        if source == "index.md":
            aliases.append("/")
        content = prepend_frontmatter(content, title, section_weights[section], sorted(set(aliases)))

        destination_path = DOCS / destination
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_text(content)
        if source_path != destination_path:
            source_path.unlink()

    shutil.rmtree(DOCS / "overrides", ignore_errors=True)


if __name__ == "__main__":
    main()
