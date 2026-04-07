# PDF Creation Plan

## Goal

Provide a standalone PDF build pipeline for the major guide trees in
`docs/content` without depending on the Hugo site build. Each guide should be
assembled from its filesystem tree, normalized for Pandoc, and rendered to a
version-aware PDF under `docs/pdf/`.

## Non-Goals

- Replacing the Hugo site build
- Expanding arbitrary Hugo shortcodes in v1
- Publishing PDFs into the site automatically
- Making content version-aware beyond output pathing

## Current Architecture

- `docs/Makefile` exposes:
  from inside `docs/`, `make pdf` relies on the existing `deps` target for
  Hugo and front-end docs tooling, and `deps` also prepares the repo-owned
  Pandoc image.
  - `make pdf`
  - `make pdf-clean`
- `docs/scripts/assemble-markdown.py` is the assembler entrypoint. It writes the
  unified Markdown build artifact for each pending guide/version pair and emits
  only the per-render paths and state metadata that vary between guides.
- `docs/scripts/mkpdf.sh` is the wrapper entrypoint. It consumes the
  assembler output and runs the Pandoc Docker container directly against the
  generated unified Markdown file, using defaults from `docs/pdf.toml` unless
  the invocation overrides them.
- `docs/pdf.toml` is the tracked PDF pipeline config and guide manifest.
- `docs/pandoc/defaults.yaml` is the default Pandoc configuration surface and
  owns the template, Lua filter list, and PDF engine selection.
- `docs/pandoc/filters/` contains semantic Pandoc Lua filters.
- `docs/pandoc/templates/guide.tex` is the default LaTeX template and visual layer.
- `docs/docker/pandoc/Dockerfile` defines the repo-owned Pandoc build image.
  It is based on `texlive/texlive` so the full TeX layer comes from a TeX-native
  base image, while Pandoc, Node, fonts, and Mermaid CLI are added on top for
  the docs-specific render path.
- Generated PDFs and caches live under `docs/pdf/`.

## File And Output Contract

- Tracked inputs:
  - `docs/pdf.toml`
  - `docs/pandoc/defaults.yaml`
  - the `docs/pandoc/` support tree referenced by `defaults.yaml`, including
    templates and filters
  - `docs/scripts/mkpdf.sh`
  - `docs/scripts/assemble-markdown.py`
- Generated outputs:
  - versioned mode: `docs/pdf/<version>/<slug>.pdf`
  - unversioned mode: `docs/pdf/<slug>.pdf`
  - caches and build scratch: `docs/pdf/.cache/`

## Versioning Contract

- `version_mode = "auto" | "explicit" | "off"` lives in `docs/pdf.toml`
- `pandoc_image`, `pandoc_dockerfile`, and `pandoc_mount_root` also live in
  `docs/pdf.toml` so the container runtime is a tracked part of the pipeline
  contract rather than a Makefile default.
- `auto` reads `[[params.versions]]` from `docs/hugo.toml`
- `auto` falls back to `latest` if no Hugo versions are configured
- `explicit` requires the builder to be invoked with `--version <value>`
- `off` writes directly to `docs/pdf/<slug>.pdf`

## Supported Content Features

- Hugo front matter for `title`, `weight`, and `description`
- Directory and page ordering by `weight`, then title, then path
- Root-relative links
- Root-relative assets
- GFM alert blocks such as `> [!NOTE]`
- Mermaid fences rendered by the diagram Lua filter through the `mmdc` binary
  installed in the repo-owned Pandoc container
- Standard Pandoc/GFM Markdown features such as tables, code fences, and
  footnotes

## Implementation Phases

### Phase 1

- Land the builder, guide manifest, template, filters, and Make targets
- Validate `design-guide.pdf`
- Make rebuild skipping work from content and template/filter changes

### Phase 2

- Tune LaTeX styling and typography via the template only
- Expand filter coverage if new Hugo-specific content patterns appear
- Decide whether generated PDFs should eventually be published by the site

## Validation Checklist

- from inside `docs/`: `make pdf`
- from inside `docs/`: `make pdf-clean`
- from inside `docs/`: `python3 scripts/assemble-markdown.py design-guide`
- from inside `docs/`: `scripts/mkpdf.sh design-guide`
- Verify `auto`, `explicit`, and `off` version modes
- Verify Mermaid diagrams render as images
- Verify same-guide links become internal anchors
- Verify out-of-guide links remain website links

## Open Issues

- The current version list in `docs/hugo.toml` is still commented out, so
  `auto` currently resolves to `latest`.
- The default LaTeX template is intentionally modest; future design work should
  stay in `docs/pandoc/templates/guide.tex` instead of moving style into
  filters.
- The full PDF runtime is now containerized. If the PDF output changes because
  the toolchain changes, that should be expressed by editing
  `docs/docker/pandoc/Dockerfile` or `docs/pdf.toml`, not by relying on host
  package drift.
- If guide content starts using Hugo shortcodes directly, v1 behavior will need
  to be revisited.

## Deferred Work

- Automatic publishing or copying of PDFs into site-served directories
- Rich title-page branding beyond the default template
- Additional asset resolution rules if the docs tree adopts more mount points
