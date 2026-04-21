# Docs Build Guide

This directory is the local Hugo site root for the Genestack documentation.
The shared documentation source lives under `/docs/content`.

Use this file for build, test, and PDF workflow information.
Authoring and style guidance lives in [STYLE_GUIDE.md](STYLE_GUIDE.md).

## Directory Layout

- `/docs/content` contains the shared Markdown source and shared documentation assets.
- `/docs` contains the Hugo config, theme wiring, build tooling, PDF tooling, and local runtime support files.
- `/docs/public` is generated Hugo site output.
- `/docs/pdf` is generated PDF output.
- `/docs/pdf/temp` is the visible scratch area for PDF assembly, state, and diagram artifacts.

## Prerequisites

- Docker
- `make`
- Python 3

The supported workflow uses containerized Hugo, containerized Pandoc, and a
containerized markdownlint runtime.
The Hugo container image is built locally from the pinned upstream Hugo image
plus the PostCSS toolchain required by Docsy production builds.
A host Hugo install is not part of the intended workflow.

Host `node` and `npm` are not required for the normal docs build, serve, lint,
or PDF workflow.
They are only needed for the optional `make setup` target used for agent-driven
browser automation work.

## Quick Start

Run these commands from `/docs`:

```sh
make deps
make serve
```

That is the fastest way to do quick structural checks while editing.

For a more realistic static-site check:

```sh
make build
docker compose up
```

That path builds the final static output into `/docs/public` and serves that
output through the Caddy container defined in [compose.yml](compose.yml).

## Fork Configuration

If you are working from a fork, update the repository URLs in
[hugo.toml](hugo.toml) before testing UI links.

At minimum, change:

```toml
[params]
github_repo = "https://github.com/<owner>/<repo>"
```

If you want the GitHub icon in the top navigation to point at the same fork,
also update the hardcoded menu entry near the bottom of `hugo.toml`:

```toml
[[menu.main]]
url = "https://github.com/<owner>/<repo>"
```

Be pedantic here: `params.github_repo` and the menu URL are two separate
settings in the current Hugo config.

## Testing Guidance

Use `make serve` for quick-and-dirty structural testing.

This is the right choice when you need fast feedback on:

- navigation placement
- section ordering
- broken front matter
- missing files
- obvious rendering mistakes

Use `make build` plus `docker compose up` for formatting and flow testing.

This is the better choice when you need to evaluate:

- full static output
- page-to-page flow
- layout and formatting in generated output
- final asset resolution from `public/`
- what a reviewer will see from the built site rather than the live Hugo server

Recommended testing loop from `/docs`:

```sh
make lint
make build
docker compose up
```

Then browse [http://localhost:1313](http://localhost:1313).

The build target also writes a sentinel file at
[public/build.txt](public/build.txt) after a
successful Hugo build. That is useful if you need to confirm that a rebuild has
finished before checking output.

## Make Targets

Run all targets from `/docs`.

### Common Targets

| Target | Purpose |
| --- | --- |
| `make deps` | Build the local Hugo runtime image and any prerequisites needed for the normal docs workflow. |
| `make build` | Build the Hugo site into `docs/public` and write `public/build.txt`. |
| `make serve` | Run the Hugo development server in the pinned container on port `1313`. |
| `make lint` | Run markdownlint against `content/**/*.md` using the dedicated markdownlint container. |
| `make pdf` | Build every configured guide PDF through the Pandoc pipeline. |
| `make pdf-clean` | Remove generated PDF artifacts and PDF scratch output. |
| `make clean` | Remove generated site output and PDF output, then restore generated docs stubs. |
| `make setup` | Optional agent-development target. Installs the local Playwright browser payload and requires host `node` and `npm`. |
| `make mrproper` | Remove all generated docs artifacts, caches, local downloads, and `node_modules`. |

### Support Targets

These are real Make targets in the current `Makefile`, but they are primarily
helper or maintainer targets rather than the everyday edit-preview loop.

| Target | Purpose |
| --- | --- |
| `make container` | Build the local Hugo runtime image that bundles Docsy's PostCSS requirements. |
| `make markdownlint-container` | Build the local markdownlint image used by `make lint`. |
| `make npm-install` | Optional helper for `make setup`. Installs the host-side Playwright tooling dependencies. |
| `make pdf-container` | Build the local Pandoc container image defined by `pdf.toml` and `docker/pandoc/Dockerfile`. |
| `make ensure-hugo-runtime` | Create the writable Hugo cache and temp-home directories expected by the container runtime. |
| `make ensure-doc-stubs` | Restore tracked generated-doc stubs when they are absent. |
| `make hugo-mod-tidy` | Run `hugo mod tidy` inside the pinned Hugo container. |

## Site Build Pipeline

The Hugo site build path is:

1. `make deps`
2. `make ensure-doc-stubs`
3. `make ensure-hugo-runtime`
4. run Hugo in the local runtime image derived from the pinned upstream Hugo base
5. write the generated site into `/docs/public`
6. write `/docs/public/build.txt`

The local development server path is similar, but `make serve` runs Hugo in
server mode instead of emitting a static site.

## Static Output Testing With Compose

[compose.yml](compose.yml) defines a minimal
Caddy container that serves `/docs/public` on port `1313`.

Use it like this:

```sh
make build
docker compose up
```

After that:

- rebuild the site with `make build` whenever content changes
- refresh the browser to inspect the new static output
- stop the server with `docker compose down`

This path is intentionally different from `make serve`.
`make serve` is faster for structure checks.
`make build` plus Compose is better for evaluating the built output as a static
site.

## PDF Build Process

The PDF workflow is configured by [pdf.toml](pdf.toml).
That file defines:

- the output root
- the Pandoc defaults file
- the Pandoc container image and Dockerfile
- the Hugo config used for metadata resolution
- the versioning mode
- the guide manifest

`make pdf` currently builds these guide PDFs directly into `/docs/pdf`:

- `overview.pdf`
- `design-guide.pdf`
- `deployment-guide.pdf`
- `operations-guide.pdf`
- `openstack-onboarding.pdf`

`test.pdf` is intentionally not part of the configured `make pdf` pipeline.
Generate it only on demand with `./scripts/mkpdf.sh test`.

The PDF scratch area lives under `/docs/pdf/temp`, including:

- assembled Markdown under `/docs/pdf/temp/build`
- state files under `/docs/pdf/temp/state`
- Mermaid image cache under `/docs/pdf/temp/mermaid`
- runtime cache directories under `/docs/pdf/temp/home` and `/docs/pdf/temp/xdg-cache`

## PDF Pipeline

The PDF pipeline has two main stages:

1. assembly
2. render

Assembly is handled by
[assemble-markdown.py](scripts/assemble-markdown.py).
It walks the configured guide tree, orders pages, flattens them into one
Pandoc-ready Markdown file, and injects document metadata such as the guide
title and version label.

Render is handled by [mkpdf.sh](scripts/mkpdf.sh).
That wrapper runs the Pandoc container against the assembled Markdown input and
writes the final PDF into `/docs/pdf`.

The Pandoc behavior itself is controlled by:

- [pandoc/defaults.yaml](pandoc/defaults.yaml)
- the Lua filters under [pandoc/filters](pandoc/filters)
- [pandoc/templates/template.latex](pandoc/templates/template.latex)

## PDF Version Label

The PDF workflow resolves the document version in `auto` mode from
`params.release` in [hugo.toml](hugo.toml).

If `params.release` is missing, the builder falls back to the current git
branch name.
If the current git branch is `main`, the fallback label is `Latest`.

The version label is metadata in the PDF document itself.
It does not create release-specific output directories under `/docs/pdf`.

## Generated Content Note

The site build restores generated-doc stubs when required through the
`ensure-doc-stubs` target. Today that primarily affects the product-matrix
page.

If generated content is missing, do not hand-create a replacement file as part
of the normal build loop. Use the tracked build targets so the generated inputs
stay consistent with the repo's intended pipeline.
