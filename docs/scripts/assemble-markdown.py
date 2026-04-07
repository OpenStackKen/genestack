#!/usr/bin/env python3
"""Assemble guide PDFs from Hugo content trees without invoking the site build.

The assembler has two responsibilities:

1. Resolve pipeline configuration and version policy from tracked repo files.
2. Flatten one or more Hugo content trees into a single Pandoc input document
   with enough metadata for Lua filters and the LaTeX template to do their work.

The script deliberately keeps formatting decisions out of Python. Python owns
content discovery, ordering, unified Markdown assembly, and hash-based rebuild
planning; the shell wrapper owns Docker image invocation and direct Pandoc
container execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import textwrap
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


# All repo-relative paths are anchored from the `docs/` tree because this
# script is a docs-local build tool, not a repo-wide content processor.
DOCS_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = DOCS_ROOT / "content"
DEFAULT_CONFIG = DOCS_ROOT / "pdf.toml"
DEFAULT_PANDOC_DEFAULTS = DOCS_ROOT / "pandoc" / "defaults.yaml"
DEFAULT_HUGO_CONFIG = DOCS_ROOT / "hugo.toml"
SITE_BASE_URL = "/"


@dataclass(frozen=True)
class GuideConfig:
    """Static guide-level config from `docs/pdf.toml`."""

    slug: str
    source: str
    output: str
    title: str


@dataclass(frozen=True)
class PagePreview:
    """Minimal metadata used only for deterministic ordering decisions."""

    weight: int
    title: str
    path_key: str


@dataclass(frozen=True)
class Page:
    """A fully normalized page ready to be flattened into the aggregate doc."""

    source_path: Path
    level: int
    title: str
    body: str
    anchor_id: str


@dataclass(frozen=True)
class PipelineConfig:
    """Tracked pipeline settings loaded from docs/pdf.toml."""

    output_dir: Path
    pandoc_defaults: Path
    pandoc_image: str
    pandoc_dockerfile: Path
    pandoc_mount_root: str
    hugo_config: Path
    version_mode: str
    site_base_url: str


@dataclass(frozen=True)
class PendingRender:
    """One pending Pandoc render produced by the assembler."""

    input_path: Path
    output_path: Path
    state_path: Path
    state_payload: str


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface the assembler keeps for local tooling use.

    The assembler is intentionally single-guide: the wrapper is responsible for
    deciding which guide slugs to build and for invoking the assembler once per
    guide.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="Guide slug to build, or `clean`")
    parser.add_argument("--config", default="pdf.toml")
    parser.add_argument(
        "--version-mode",
        choices=("auto", "explicit", "off"),
        help="Override the version mode from pdf.toml",
    )
    parser.add_argument("--version", help="Explicit version label")
    parser.add_argument("--pandoc-defaults", help="Override the pandoc defaults path from pdf.toml")
    parser.add_argument("--pandoc-image", help="Override the pandoc image from pdf.toml")
    parser.add_argument("--pandoc-mount-root", help="Override the pandoc mount root from pdf.toml")
    args = parser.parse_args()
    if args.target == "help":
        parser.print_help()
        raise SystemExit(0)
    return args


def main() -> int:
    # `main()` is intentionally thin: it resolves tracked configuration for one
    # guide invocation and emits one shell-consumable render record per version
    # that still requires a Pandoc render.
    args = parse_args()
    pipeline_config = load_pipeline_config(resolve_docs_path(args.config))
    # Runtime overrides deliberately stay narrow. The assembler still treats
    # `pdf.toml` as the source of truth, but the wrapper can override the few
    # container-facing values that are useful during local debugging.
    effective_defaults_path = resolve_docs_path(args.pandoc_defaults) if args.pandoc_defaults else pipeline_config.pandoc_defaults
    effective_mount_root = args.pandoc_mount_root or pipeline_config.pandoc_mount_root
    effective_image = args.pandoc_image or pipeline_config.pandoc_image
    pipeline_config = PipelineConfig(
        output_dir=pipeline_config.output_dir,
        pandoc_defaults=effective_defaults_path,
        pandoc_image=effective_image,
        pandoc_dockerfile=pipeline_config.pandoc_dockerfile,
        pandoc_mount_root=effective_mount_root,
        hugo_config=pipeline_config.hugo_config,
        version_mode=pipeline_config.version_mode,
        site_base_url=pipeline_config.site_base_url,
    )
    manifest = load_manifest(resolve_docs_path(args.config))
    output_root = pipeline_config.output_dir
    cache_root = output_root / ".cache"

    if args.target == "clean":
        # `clean` intentionally reuses the same config load path as normal
        # builds, so it removes only outputs that belong to the currently
        # configured guide set and output directory.
        clean_generated_outputs(output_root, cache_root, manifest)
        return 0

    defaults_path = pipeline_config.pandoc_defaults
    if not defaults_path.is_file():
        raise SystemExit(f"pandoc defaults file not found: {defaults_path}")

    version_mode = args.version_mode or pipeline_config.version_mode
    versions = resolve_versions(pipeline_config.hugo_config, version_mode, args.version)
    pending_renders: list[PendingRender] = []
    # The wrapper is responsible for multi-guide expansion. By the time
    # execution reaches this point, the assembler is working on exactly one
    # guide slug and one version policy.
    guide_slug = select_guide(args.target, manifest)
    pending_renders.extend(
        plan_one_guide(
            guide=manifest[guide_slug],
            versions=versions,
            output_root=output_root,
            cache_root=cache_root,
            config_path=resolve_docs_path(args.config),
            manifest_path=resolve_docs_path(args.config),
            hugo_config_path=pipeline_config.hugo_config,
            defaults_path=defaults_path,
            pandoc_dockerfile_path=pipeline_config.pandoc_dockerfile,
            pandoc_image=pipeline_config.pandoc_image,
            pandoc_mount_root=pipeline_config.pandoc_mount_root,
            version_mode=version_mode,
            site_base_url=pipeline_config.site_base_url,
            pipeline_config=pipeline_config,
        )
    )

    emit_pending_renders(pending_renders)

    return 0


def resolve_docs_path(raw_path: str) -> Path:
    """Resolve a path relative to `docs/` unless the caller supplied an absolute path."""

    path = Path(raw_path)
    if path.is_absolute():
        return path
    return DOCS_ROOT / path


def load_pipeline_config(path: Path) -> PipelineConfig:
    """Load tracked pipeline settings from docs/pdf.toml.

    Keeping these settings in TOML rather than Make variables makes the PDF
    pipeline reproducible and easier to inspect in code review. The assembler
    still allows a few CLI overrides where the caller needs to choose a build
    scope or a one-off explicit version.
    """

    if not path.is_file():
        raise SystemExit(f"pdf config not found: {path}")

    with path.open("rb") as handle:
        data = tomllib.load(handle)

    version_mode = data.get("version_mode", "auto")
    if version_mode not in {"auto", "explicit", "off"}:
        raise SystemExit(f"unsupported version_mode in {path}: {version_mode}")

    return PipelineConfig(
        output_dir=resolve_docs_path(data.get("output_dir", "pdf")),
        pandoc_defaults=resolve_docs_path(data.get("pandoc_defaults", str(DEFAULT_PANDOC_DEFAULTS.relative_to(DOCS_ROOT)))),
        pandoc_image=data.get("pandoc_image", "genestack-docs-pandoc:latest"),
        pandoc_dockerfile=resolve_docs_path(data.get("pandoc_dockerfile", "docker/pandoc/Dockerfile")),
        pandoc_mount_root=data.get("pandoc_mount_root", "/docs"),
        hugo_config=resolve_docs_path(data.get("hugo_config", str(DEFAULT_HUGO_CONFIG.relative_to(DOCS_ROOT)))),
        version_mode=version_mode,
        site_base_url=data.get("site_base_url", SITE_BASE_URL),
    )


def load_manifest(path: Path) -> dict[str, GuideConfig]:
    """Load the curated guide allowlist and output mapping from `docs/pdf.toml`."""

    with path.open("rb") as handle:
        data = tomllib.load(handle)

    manifest: dict[str, GuideConfig] = {}
    for guide_entry in data.get("guides", []):
        # The manifest is intentionally explicit. The builder only processes
        # guides named here; walking arbitrary top-level content directories is
        # out of scope because PDF output is meant to be curated.
        guide = GuideConfig(
            slug=guide_entry["slug"],
            source=guide_entry["source"],
            output=guide_entry["output"],
            title=guide_entry["title"],
        )
        manifest[guide.slug] = guide

    if not manifest:
        raise SystemExit(f"guide manifest is empty: {path}")
    return manifest


def select_guide(target: str, manifest: dict[str, GuideConfig]) -> str:
    """Resolve a single guide slug from CLI arguments against the manifest."""

    # `help` is handled in `parse_args()` so anything reaching this function
    # must either be a valid guide slug or an error worth surfacing clearly.
    if target not in manifest:
        valid = ", ".join(sorted(manifest))
        raise SystemExit(f"unknown guide '{target}'. valid guides: {valid}")
    return target


def resolve_versions(config_path: Path, mode: str, explicit_version: str | None) -> list[str | None]:
    """Resolve version labels from Hugo config plus caller intent.

    `auto` mirrors Hugo's version list when present and falls back to `latest`
    when the docs site has not enabled versioning yet.
    """

    if mode == "off":
        return [None]
    if mode == "explicit":
        if not explicit_version:
            raise SystemExit("--version is required when --version-mode=explicit")
        return [explicit_version]

    # `auto` follows Hugo’s notion of versions so the PDF pipeline and the site
    # can stay aligned without duplicating version lists in separate files.
    with config_path.open("rb") as handle:
        data = tomllib.load(handle)

    params = data.get("params", {})
    versions = params.get("versions", [])
    if not versions:
        return ["latest"]

    labels = [entry.get("version", "").strip() for entry in versions if isinstance(entry, dict)]
    labels = [label for label in labels if label]
    return labels or ["latest"]


def emit_pending_renders(pending_renders: list[PendingRender]) -> None:
    """Write pending render records to stdout in a shell-friendly format."""

    # The wrapper intentionally consumes a tiny, line-oriented contract:
    # unified Markdown path, final PDF path, state file path, and state JSON.
    # Keeping this output flat makes it easy to inspect manually and avoids
    # dragging container runtime details into Python.
    for render in pending_renders:
        output_label = (
            str(render.output_path.relative_to(DOCS_ROOT))
            if render.output_path.is_absolute() and DOCS_ROOT in render.output_path.parents
            else str(render.output_path)
        )
        input_label = (
            str(render.input_path.relative_to(DOCS_ROOT))
            if render.input_path.is_absolute() and DOCS_ROOT in render.input_path.parents
            else str(render.input_path)
        )
        print(f"[assemble] planned: {output_label} <- {input_label}", file=sys.stderr)
        print(
            "\t".join(
                [
                    str(render.input_path),
                    str(render.output_path),
                    str(render.state_path),
                    render.state_payload,
                ]
            )
        )


def plan_one_guide(
    *,
    guide: GuideConfig,
    versions: list[str | None],
    output_root: Path,
    cache_root: Path,
    config_path: Path,
    manifest_path: Path,
    hugo_config_path: Path,
    defaults_path: Path,
    pandoc_dockerfile_path: Path,
    pandoc_image: str,
    pandoc_mount_root: str,
    version_mode: str,
    site_base_url: str,
    pipeline_config: PipelineConfig,
) -> list[PendingRender]:
    """Assemble one guide across one or more version labels.

    The assembler writes the combined Markdown first, then compares a manifest
    hash before emitting a small render record for the shell wrapper. That
    keeps rebuild checks deterministic while moving Docker orchestration out of
    Python.
    """

    guide_root = DOCS_ROOT / guide.source
    if not guide_root.is_dir():
        raise SystemExit(f"guide source directory does not exist: {guide_root}")

    pending_renders: list[PendingRender] = []
    for version_label in versions:
        # The unified Markdown artifact is written even when the later PDF
        # render is skipped. That makes the assembled input easy to inspect
        # during debugging without forcing a separate "dump assembled markdown"
        # mode into the CLI.
        assembled = assemble_guide_markdown(
            guide,
            guide_root,
            version_label,
            docs_root_for_pandoc=pipeline_config.pandoc_mount_root,
            site_base_url=site_base_url,
        )
        output_path = output_pdf_path(output_root, guide, version_label)
        build_markdown_path = cache_root / "build" / build_key(version_label, guide.slug) / f"{guide.slug}.md"
        state_path = cache_root / "state" / build_key(version_label, guide.slug) / f"{guide.slug}.json"
        manifest_hash = compute_manifest_hash(
            guide_root=guide_root,
            version_label=version_label,
            output_path=output_path,
            config_path=config_path,
            manifest_path=manifest_path,
            hugo_config_path=hugo_config_path,
            defaults_path=defaults_path,
            pandoc_dockerfile_path=pandoc_dockerfile_path,
            pandoc_image=pandoc_image,
            pandoc_mount_root=pandoc_mount_root,
            version_mode=version_mode,
        )

        prior_hash = read_prior_hash(state_path)
        if prior_hash == manifest_hash and output_path.is_file():
            print(f"[pdf] up to date: {output_path.relative_to(DOCS_ROOT)}", file=sys.stderr)
            continue

        # The wrapper writes the state file only after Pandoc succeeds. The
        # assembler therefore prepares the state payload here but does not mark
        # the render complete on its own.
        build_markdown_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        build_markdown_path.write_text(assembled, encoding="utf-8")
        pending_renders.append(
            PendingRender(
                input_path=build_markdown_path,
                output_path=output_path,
                state_path=state_path,
                state_payload=json.dumps(
                    {
                        "hash": manifest_hash,
                        "output": str(output_path.relative_to(DOCS_ROOT)),
                        "version": version_label or "",
                        "guide": guide.slug,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            )
        )

    return pending_renders


def assemble_guide_markdown(
    guide: GuideConfig,
    guide_root: Path,
    version_label: str | None,
    *,
    docs_root_for_pandoc: str,
    site_base_url: str,
) -> str:
    """Flatten a guide tree into a single Pandoc-ready Markdown document.

    The YAML metadata block is intentionally the hand-off point for cross-tool
    configuration. Filters read pathing and cache settings from metadata rather
    than from Make-time environment variables so the generated input document is
    self-describing.
    """

    pages = collect_pages(guide, guide_root)
    # Section headings are emitted separately from page bodies so the PDF gets
    # a stable top-level structure even when individual source files omit a
    # first heading.
    rendered_pages: list[str] = []
    next_footnote_number = 1
    for index, page in enumerate(pages):
        if not (page.body.strip() or page.level >= 1):
            continue
        # Footnotes are renumbered before render so independent source files
        # can all use local labels like `[^1]` without colliding after the
        # guide is flattened into one document.
        normalized_body, next_footnote_number = renumber_footnotes(page.body, start_number=next_footnote_number)
        # The document title already comes from the aggregate YAML metadata, so
        # the root landing page should not repeat that same guide title as the
        # first visible heading in the combined Markdown.
        suppress_heading = index == 0 and page.level == 1 and page.anchor_id == guide.slug
        rendered_pages.append(render_page(page, body=normalized_body, suppress_heading=suppress_heading))
    content = "\n\n".join(rendered_pages)
    metadata = textwrap.dedent(
        f"""\
        ---
        title: "{escape_yaml_scalar(guide.title)}"
        version: "{escape_yaml_scalar(version_label or '')}"
        guide_slug: "{guide.slug}"
        docs_root: "{escape_yaml_scalar(docs_root_for_pandoc)}"
        site_base_url: "{escape_yaml_scalar(site_base_url)}"
        version_label: "{escape_yaml_scalar(version_label or '')}"
        ---
        """
    )
    return metadata + "\n" + content + "\n"


def collect_pages(guide: GuideConfig, guide_root: Path) -> list[Page]:
    """Walk the guide tree and return pages in the final document order."""

    pages: list[Page] = []
    # The walk starts at `.` so depth calculation can map the filesystem tree
    # onto heading levels without any special case for the guide root.
    walk_directory(guide_root, Path("."), guide.slug, pages)
    if not pages:
        raise SystemExit(f"guide '{guide.slug}' does not contain any Markdown pages")
    return pages


def walk_directory(directory: Path, rel_dir: Path, guide_slug: str, pages: list[Page]) -> None:
    """Traverse a guide tree using Hugo-style section semantics where present.

    `_index.md` is treated as the section opener for a directory. Sibling
    directories and pages are ordered by `weight`, then title, then path so the
    flattened PDF stays stable when metadata is incomplete.
    """

    current_depth = 0 if rel_dir == Path(".") else len(rel_dir.parts)
    index_path = directory / "_index.md"
    if index_path.is_file():
        # `_index.md` behaves like a Hugo section landing page, so it becomes
        # the first heading for that directory level.
        pages.append(parse_page(index_path, guide_slug, current_depth + 1))

    entries = [entry for entry in directory.iterdir() if not entry.name.startswith(".")]
    entries = [entry for entry in entries if entry.name != "_index.md"]
    # Python’s sort is stable, so sorting least-significant key first gives us
    # Hugo-like weight ordering with deterministic tie-breakers.
    entries.sort(key=lambda entry: preview_for_entry(entry).path_key)
    entries.sort(key=lambda entry: preview_for_entry(entry).title.lower())
    entries.sort(key=lambda entry: preview_for_entry(entry).weight)

    for entry in entries:
        if entry.is_dir():
            walk_directory(entry, rel_dir / entry.name, guide_slug, pages)
        elif entry.suffix == ".md":
            pages.append(parse_page(entry, guide_slug, current_depth + 2))


def preview_for_entry(entry: Path) -> PagePreview:
    """Read just enough metadata from an entry to place it in the final order."""

    # Sorting a large tree should not require parsing every full page body.
    # This helper reads only the shallow metadata needed to determine where the
    # entry lands in the flattened guide order.
    metadata_source = entry / "_index.md" if entry.is_dir() else entry
    if metadata_source.is_file():
        metadata, _ = parse_markdown_file(metadata_source)
    else:
        metadata = {}
    title = metadata.get("title") or fallback_title(entry)
    return PagePreview(
        weight=parse_weight(metadata.get("weight")),
        title=title,
        path_key=str(entry),
    )


def parse_page(path: Path, guide_slug: str, level: int) -> Page:
    """Convert a source Markdown file into a page entry for the aggregate doc."""

    # Parsing and normalization happen before render so later stages can work
    # against one predictable in-memory shape rather than repeatedly deriving
    # titles, anchors, and adjusted heading bodies.
    metadata, body = parse_markdown_file(path)
    title = metadata.get("title") or fallback_title(path)
    site_path = hugo_site_path(path, guide_slug)
    anchor_id = anchor_for_site_path(site_path)
    return Page(
        source_path=path,
        level=level,
        title=title,
        # In-page headings are rewritten before aggregation so every heading id
        # is already stable when Pandoc resolves links and LaTeX labels.
        body=annotate_headings(body, anchor_id),
        anchor_id=anchor_id,
    )


def parse_markdown_file(path: Path) -> tuple[dict[str, Any], str]:
    """Split a Markdown file into shallow front matter metadata and body text.

    The front matter parser is intentionally narrow because the builder only
    needs a small set of keys to determine ordering and page titles.
    """

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text.strip()

    fence = "\n---\n"
    end_index = text.find(fence, 4)
    if end_index == -1:
        return {}, text.strip()

    frontmatter = text[4:end_index]
    body = text[end_index + len(fence) :]
    return parse_yaml_frontmatter(frontmatter), body.strip()


def parse_yaml_frontmatter(frontmatter: str) -> dict[str, Any]:
    """Parse the simple scalar subset of front matter the builder cares about.

    This is intentionally not a general YAML parser. The PDF builder only
    depends on a few shallow keys for ordering and titling, so keeping the
    parser narrow makes its behavior easier to reason about.
    """

    metadata: dict[str, Any] = {}
    for line in frontmatter.splitlines():
        if not line or line.startswith("#") or line.startswith(" ") or line.startswith("\t"):
            continue
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        metadata[key.strip()] = parse_scalar(raw_value.strip())
    return metadata


def parse_scalar(raw_value: str) -> Any:
    """Parse the small scalar shapes the shallow front matter reader accepts."""

    if not raw_value:
        return ""
    if raw_value.startswith(("'", '"')) and raw_value.endswith(raw_value[0]) and len(raw_value) >= 2:
        return raw_value[1:-1]
    if re.fullmatch(r"-?\d+", raw_value):
        return int(raw_value)
    return raw_value


def parse_weight(value: Any) -> int:
    """Normalize `weight` so unweighted entries sort after weighted ones."""

    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.fullmatch(r"-?\d+", value):
        return int(value)
    return 10_000


def fallback_title(path: Path) -> str:
    """Build a human-readable title when front matter omits one."""

    candidate = path.parent.name if path.name == "_index.md" else path.stem
    return candidate.replace("-", " ").replace("_", " ").title()


def hugo_site_path(path: Path, guide_slug: str) -> str:
    """Recreate the Hugo-style site path for a content file.

    The path model is reused for anchor generation and same-guide link
    rewriting so the PDF can behave like a flattened view of the site.
    """

    rel_path = path.relative_to(CONTENT_ROOT / guide_slug)
    if path.name == "_index.md":
        parts = list(rel_path.parent.parts)
    else:
        parts = list(rel_path.with_suffix("").parts)
    parts = [guide_slug] + [part for part in parts if part != "."]
    return "/" + "/".join(parts) + "/"


def anchor_for_site_path(site_path: str) -> str:
    """Collapse a site path into the stable anchor base for that page."""

    parts = [part for part in site_path.strip("/").split("/") if part]
    return slugify("-".join(parts))


def slugify(text: str) -> str:
    """Generate a conservative ASCII id that is safe for Markdown and LaTeX."""

    lowered = text.lower()
    lowered = re.sub(r"[^\w\s-]", "", lowered, flags=re.ASCII)
    lowered = lowered.replace("_", "-")
    lowered = re.sub(r"\s+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered)
    return lowered.strip("-") or "section"


def promote_heading_level(level: int) -> int:
    """Promote one aggregate heading level, with `#` as the ceiling.

    The flattened PDF tends to accumulate one extra level of indentation
    because section opener pages and their in-page headings are both rendered
    into the same document. Promoting all emitted headings by one level keeps
    the aggregate structure tighter without introducing an impossible heading
    level above `#`.
    """

    return max(level - 1, 1)


def annotate_headings(body: str, page_anchor: str) -> str:
    """Rewrite in-page headings with stable, page-scoped anchor ids.

    Pandoc will happily accept duplicate identifiers, but LaTeX then emits
    multiply-defined label warnings. Keeping anchor generation page-scoped and
    de-duplicated avoids that class of noisy and fragile PDF output.
    """

    if not body:
        return ""

    annotated: list[str] = []
    heading_counts: dict[str, int] = {}
    in_fence = False
    fence_marker = ""
    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        fence_match = re.match(r"^(```+|~~~+)", line)
        if fence_match:
            # Headings inside fenced code should remain literal code, not become
            # document structure, so the fence state is tracked explicitly.
            marker = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker[0]
            elif marker[0] == fence_marker:
                in_fence = False
                fence_marker = ""
            annotated.append(line)
            continue

        if in_fence:
            annotated.append(line)
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if not heading_match or "{#" in line:
            annotated.append(line)
            continue

        # Each source page is still nested under a generated page heading in
        # the aggregate document, so the source heading level is first shifted
        # down by one. The aggregate-level promotion pass then pulls the whole
        # combined outline back up by one level, with `#` as the ceiling.
        level = promote_heading_level(min(len(heading_match.group(1)) + 1, 6))
        heading_text = strip_closing_hashes(heading_match.group(2))
        base_id = f"{page_anchor}--{slugify(strip_inline_markdown(heading_text))}"
        occurrence = heading_counts.get(base_id, 0) + 1
        heading_counts[base_id] = occurrence
        heading_id = base_id if occurrence == 1 else f"{base_id}-{occurrence}"
        annotated.append(f"{'#' * level} {heading_text} {{#{heading_id}}}")

    return "\n".join(annotated).strip()


def strip_closing_hashes(text: str) -> str:
    """Remove optional closing ATX heading markers before slug generation."""

    return re.sub(r"\s+#+\s*$", "", text).strip()


def strip_inline_markdown(text: str) -> str:
    """Approximate a plain-text heading value before slug generation."""

    stripped = re.sub(r"`([^`]*)`", r"\1", text)
    stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)
    stripped = re.sub(r"[*_~]", "", stripped)
    return stripped


def renumber_footnotes(body: str, *, start_number: int) -> tuple[str, int]:
    """Rewrite footnote labels into one guide-wide numeric sequence.

    Source pages are authored independently, so local labels like `[^1]` are
    common and perfectly reasonable in the Hugo tree. Once those pages are
    flattened into one Markdown document, those local labels collide and can
    merge unrelated notes. The assembler therefore rewrites each page's
    footnote references and definitions into a single monotonically increasing
    sequence across the aggregate document.
    """

    if not body:
        return "", start_number

    next_number = start_number
    label_map: dict[str, str] = {}
    rewritten: list[str] = []
    in_fence = False
    fence_marker = ""

    def assign_label(label: str) -> str:
        nonlocal next_number
        if label not in label_map:
            label_map[label] = str(next_number)
            next_number += 1
        return label_map[label]

    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        fence_match = re.match(r"^(```+|~~~+)", line)
        if fence_match:
            marker = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker[0]
            elif marker[0] == fence_marker:
                in_fence = False
                fence_marker = ""
            rewritten.append(line)
            continue

        if in_fence:
            rewritten.append(line)
            continue

        definition_match = re.match(r"^(\s{0,3})\[\^([^\]]+)\]:(.*)$", line)
        if definition_match:
            indent, label, remainder = definition_match.groups()
            numbered_label = assign_label(label)
            remainder = rewrite_footnote_references(remainder, assign_label)
            rewritten.append(f"{indent}[^{numbered_label}]:{remainder}")
            continue

        rewritten.append(rewrite_footnote_references(line, assign_label))

    return "\n".join(rewritten).strip(), next_number


def rewrite_footnote_references(text: str, assign_label: Callable[[str], str]) -> str:
    """Rename footnote references while leaving inline code spans untouched."""

    rewritten: list[str] = []
    cursor = 0
    while cursor < len(text):
        if text[cursor] != "`":
            next_tick = text.find("`", cursor)
            if next_tick == -1:
                next_tick = len(text)
            segment = text[cursor:next_tick]
            segment = re.sub(r"\[\^([^\]]+)\]", lambda match: f"[^{assign_label(match.group(1))}]", segment)
            rewritten.append(segment)
            cursor = next_tick
            continue

        tick_end = cursor
        while tick_end < len(text) and text[tick_end] == "`":
            tick_end += 1
        marker = text[cursor:tick_end]
        closing = text.find(marker, tick_end)
        if closing == -1:
            rewritten.append(text[cursor:])
            break
        rewritten.append(text[cursor : closing + len(marker)])
        cursor = closing + len(marker)

    return "".join(rewritten)


def render_page(page: Page, *, body: str | None = None, suppress_heading: bool = False) -> str:
    """Render one normalized page into its final aggregate Markdown fragment."""

    page_body = page.body if body is None else body
    heading = f"{'#' * promote_heading_level(page.level)} {page.title} {{#{page.anchor_id}}}"
    if suppress_heading:
        anchor = f"[]{{#{page.anchor_id}}}"
        if not page_body:
            return anchor
        return f"{anchor}\n\n{page_body}"
    if not page_body:
        return heading
    return f"{heading}\n\n{page_body}"


def compute_manifest_hash(
    *,
    guide_root: Path,
    version_label: str | None,
    output_path: Path,
    config_path: Path,
    manifest_path: Path,
    hugo_config_path: Path,
    defaults_path: Path,
    pandoc_dockerfile_path: Path,
    pandoc_image: str,
    pandoc_mount_root: str,
    version_mode: str,
) -> str:
    """Hash every tracked input that should force a rebuild.

    The output PDF is considered stale not only when content changes, but also
    when the pipeline config, guide manifest, Hugo version config, Pandoc
    defaults, the surrounding Pandoc layout tree, or the builder itself
    changes.
    """

    hasher = hashlib.sha256()
    pandoc_root = defaults_path.parent
    manifest_inputs: Iterable[Path] = (
        config_path,
        manifest_path,
        defaults_path,
        hugo_config_path,
        pandoc_dockerfile_path,
        Path(__file__).resolve(),
    )
    # These are the top-level tracked inputs whose content directly changes the
    # shape, scope, or rendering policy of the output PDF.
    for path in manifest_inputs:
        update_hash_with_file(hasher, path)

    # The rest of the Pandoc tree is discovered from the filesystem instead of
    # being named here. That keeps the builder generic: new filters, templates,
    # or support assets automatically become part of the rebuild contract.
    for path in iter_layout_files(pandoc_root):
        if path == defaults_path:
            continue
        update_hash_with_file(hasher, path)

    # Source Markdown files are the primary content inputs. Added or removed
    # files naturally affect the hash because the directory walk changes.
    for source in sorted(guide_root.rglob("*.md")):
        update_hash_with_file(hasher, source)

    # Version mode and output path both influence the observable build result,
    # so they are part of the cache key even though they are not file inputs.
    hasher.update(str(version_label or "").encode("utf-8"))
    hasher.update(str(output_path).encode("utf-8"))
    hasher.update(pandoc_image.encode("utf-8"))
    hasher.update(pandoc_mount_root.encode("utf-8"))
    hasher.update(version_mode.encode("utf-8"))
    return hasher.hexdigest()


def update_hash_with_file(hasher: hashlib._hashlib.HASH, path: Path) -> None:
    """Hash both the path and the file bytes so renames also trigger rebuilds."""

    hasher.update(str(path.relative_to(DOCS_ROOT)).encode("utf-8"))
    hasher.update(path.read_bytes())


def iter_layout_files(root: Path) -> Iterable[Path]:
    """Yield tracked Pandoc support files from the configured layout tree.

    The builder should not care which specific filters or templates exist. It
    only needs to know that anything under the configured Pandoc tree can alter
    the rendered PDF and therefore should participate in rebuild detection.
    Hidden files are skipped so editor swap files and similar noise do not
    trigger unnecessary work.
    """

    if not root.exists():
        return []

    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and not any(part.startswith(".") for part in path.relative_to(root).parts)
    )


def read_prior_hash(state_path: Path) -> str | None:
    """Read the previous manifest hash, tolerating missing or corrupt state."""

    if not state_path.is_file():
        return None
    try:
        return json.loads(state_path.read_text(encoding="utf-8")).get("hash")
    except json.JSONDecodeError:
        return None


def output_pdf_path(output_root: Path, guide: GuideConfig, version_label: str | None) -> Path:
    """Resolve the final PDF path from the configured versioning mode outcome."""

    if version_label:
        return output_root / version_label / guide.output
    return output_root / guide.output


def build_key(version_label: str | None, guide_slug: str) -> str:
    """Create a stable cache directory key for one guide/version build."""

    return version_label or f"off-{guide_slug}"


def clean_generated_outputs(
    output_root: Path,
    cache_root: Path,
    manifest: dict[str, GuideConfig],
) -> None:
    """Remove generated PDFs and scratch state without touching tracked inputs."""

    # Cleaning is intentionally conservative: only generated PDFs and cache
    # state are removed. The tracked pipeline config, template tree, and guide
    # manifest all stay untouched so the next build starts from a known source
    # state.
    if cache_root.exists():
        shutil.rmtree(cache_root)

    # Unversioned outputs live directly under `docs/pdf/`, so remove those
    # explicitly before sweeping version directories.
    for guide in manifest.values():
        unversioned_output = output_root / guide.output
        if unversioned_output.exists():
            unversioned_output.unlink()

    if not output_root.exists():
        return

    for child in output_root.iterdir():
        if child.name == ".cache":
            continue
        if child.is_dir():
            shutil.rmtree(child)


def escape_yaml_scalar(value: str) -> str:
    """Escape a value for safe embedding in the generated YAML front matter."""

    return value.replace("\\", "\\\\").replace('"', '\\"')


if __name__ == "__main__":
    raise SystemExit(main())
