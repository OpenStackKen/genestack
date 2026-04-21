SHELL := /bin/bash

# Keep every docs-specific cache and download inside /docs so `mrproper`
# can return the tree to a source-only state without touching user-global
# tool state.
export XDG_CACHE_HOME := $(CURDIR)/.cache
export HUGO_CACHEDIR := $(CURDIR)/.cache/hugo_cache
export NPM_CONFIG_CACHE := $(CURDIR)/.npm-cache
export npm_config_cache := $(NPM_CONFIG_CACHE)
export PLAYWRIGHT_BROWSERS_PATH := $(CURDIR)/.playwright-browsers

DOCKER ?= docker
NPM ?= npm
PYTHON ?= python3
REPO_ROOT := $(abspath $(CURDIR)/..)
CONTAINER_WORKDIR := /work
HUGO_IMAGE ?= ghcr.io/gohugoio/hugo:v0.160.1@sha256:b4f4cd51ce64c7257bf103ecf8fb14f37ea7ca1980bcaaf516cdf95b14446fd7
MARKDOWNLINT_IMAGE ?= genestack-docs-markdownlint:0.21.0
HUGO_CONTAINER_HOME := $(CONTAINER_WORKDIR)/docs/.tmp-home/hugo
HUGO_RUN = $(DOCKER) run --rm \
    --name hugo \
	--user $$(id -u):$$(id -g) \
	--volume $(REPO_ROOT):$(CONTAINER_WORKDIR) \
	--workdir $(CONTAINER_WORKDIR)/docs \
	--entrypoint hugo \
	--env HOME=$(HUGO_CONTAINER_HOME) \
	--env XDG_CACHE_HOME=$(CONTAINER_WORKDIR)/docs/.cache \
	--env HUGO_CACHEDIR=$(CONTAINER_WORKDIR)/docs/.cache/hugo_cache \
	$(HUGO_IMAGE)
HUGO_RUN_SERVER = $(DOCKER) run --rm \
    --name hugo \
	--user $$(id -u):$$(id -g) \
	--volume $(REPO_ROOT):$(CONTAINER_WORKDIR) \
	--workdir $(CONTAINER_WORKDIR)/docs \
	--publish 1313:1313 \
	--entrypoint hugo \
	--env HOME=$(HUGO_CONTAINER_HOME) \
	--env XDG_CACHE_HOME=$(CONTAINER_WORKDIR)/docs/.cache \
	--env HUGO_CACHEDIR=$(CONTAINER_WORKDIR)/docs/.cache/hugo_cache \
	$(HUGO_IMAGE)
BUILD_SENTINEL := public/build.txt
PRODUCT_MATRIX_PAGE := content/overview/product-matrix.md
PRODUCT_MATRIX_STUB := scripts/product-matrix.stub.md
PDF_BUILDER := scripts/mkpdf.sh
PDF_PANDOC_IMAGE := $(shell $(PYTHON) -c 'import pathlib, tomllib; print(tomllib.loads(pathlib.Path("pdf.toml").read_text(encoding="utf-8"))["pandoc_image"])')
PDF_PANDOC_DOCKERFILE := $(shell $(PYTHON) -c 'import pathlib, tomllib; print(tomllib.loads(pathlib.Path("pdf.toml").read_text(encoding="utf-8"))["pandoc_dockerfile"])')
PDF_PANDOC_CONTEXT := $(dir $(PDF_PANDOC_DOCKERFILE))
PDF_PANDOC_IMAGE_STAMP := .cache/pdf-pandoc-image.stamp
MARKDOWNLINT_DOCKERFILE := docker/markdownlint/Dockerfile
MARKDOWNLINT_CONTEXT := $(dir $(MARKDOWNLINT_DOCKERFILE))
MARKDOWNLINT_IMAGE_STAMP := .cache/markdownlint-image.stamp
.DEFAULT_GOAL := build

.PHONY: container markdownlint-container npm-install hugo-mod-tidy deps build clean ensure-doc-stubs ensure-hugo-runtime lint mrproper pdf pdf-clean pdf-container serve setup

# Download everything required for the normal site build workflow: the pinned
# Hugo runtime image only. Host npm tooling is optional and reserved for
# `make setup`.
deps: container

# Human-friendly alias for ensuring the pinned Hugo runtime image is available
# locally before any site build or preview starts.
container:
	@if ! $(DOCKER) image inspect $(HUGO_IMAGE) >/dev/null 2>&1; then \
		$(DOCKER) pull $(HUGO_IMAGE); \
	fi

# Human-friendly alias for the file-backed markdownlint image artifact.
markdownlint-container: $(MARKDOWNLINT_IMAGE_STAMP)

# Human-friendly alias for the file-backed Pandoc image build artifact.
pdf-container: $(PDF_PANDOC_IMAGE_STAMP)

# Ensure the writable directories mounted into the Hugo container already
# exist so the runtime does not need to create them from scratch.
ensure-hugo-runtime:
	@mkdir -p .cache/hugo_cache .tmp-home/hugo

# Reconcile Hugo module metadata explicitly through the same containerized Hugo
# runtime used for ordinary builds. This is maintainer work, not part of `deps`.
hugo-mod-tidy: container ensure-hugo-runtime
	$(HUGO_RUN) mod tidy

# The stamp records that the local markdownlint image was built from the
# current Dockerfile input. When this target is newer than those inputs, `make`
# can skip `docker build` entirely for later lint runs.
$(MARKDOWNLINT_IMAGE_STAMP): $(MARKDOWNLINT_DOCKERFILE)
	@mkdir -p $(dir $@)
	$(DOCKER) build --tag $(MARKDOWNLINT_IMAGE) --file $(MARKDOWNLINT_DOCKERFILE) $(MARKDOWNLINT_CONTEXT)
	@touch $@

# The stamp records that the local Pandoc image was built from the current
# Dockerfile/config inputs. When this target is newer than those inputs, `make`
# can skip `docker build` entirely for normal docs and PDF runs.
$(PDF_PANDOC_IMAGE_STAMP): $(PDF_PANDOC_DOCKERFILE) pdf.toml
	@mkdir -p $(dir $@)
	$(DOCKER) build --tag $(PDF_PANDOC_IMAGE) --file $(PDF_PANDOC_DOCKERFILE) $(PDF_PANDOC_CONTEXT)
	@touch $@

# Install the optional host-side Playwright tooling used only for agent-driven
# browser automation work under `make setup`.
npm-install: package.json
	@command -v $(NPM) >/dev/null 2>&1 || { \
		echo "make setup is optional and requires host npm/node."; \
		exit 1; \
	}
	$(NPM) install

# Restore tracked docs stubs when generated pages are absent.
ensure-doc-stubs:
	@test -f $(PRODUCT_MATRIX_PAGE) || cp $(PRODUCT_MATRIX_STUB) $(PRODUCT_MATRIX_PAGE)

# Build the static site from the Hugo root in /docs, then atomically write a
# simple post-build sentinel that can be polled at `/build.txt`.
build: deps ensure-doc-stubs ensure-hugo-runtime
	$(HUGO_RUN)
	@mkdir -p public
	@tmp_file="$$(mktemp public/.build.txt.XXXXXX)"; \
	printf 'build_time_utc=%s\nbuild_epoch=%s\n' \
	  "$$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
	  "$$(date -u +%s)" > "$$tmp_file"; \
	mv "$$tmp_file" $(BUILD_SENTINEL)

# Hugo does not provide a standalone `clean` subcommand for site output.
# This target removes local site and PDF build output and restores generated
# docs pages back to their checked-in stub form.
clean: pdf-clean
	rm -rf public resources .hugo_build.lock
	cp $(PRODUCT_MATRIX_STUB) $(PRODUCT_MATRIX_PAGE)

# Convenience target for validating the shared Markdown sources in
# /docs/content using the docs markdownlint configuration.
lint: markdownlint-container
	$(DOCKER) run --rm \
		--user $$(id -u):$$(id -g) \
		--volume $(REPO_ROOT):$(CONTAINER_WORKDIR) \
		--workdir $(CONTAINER_WORKDIR)/docs \
		$(MARKDOWNLINT_IMAGE) \
		"content/**/*.md"

# Build every configured guide PDF. The Python assembler writes unified
# Markdown build artifacts and the shell wrapper runs the Pandoc container
# against those generated inputs.
pdf: deps pdf-container ensure-doc-stubs
	$(PDF_BUILDER) all

# Remove only generated PDF artifacts and scratch caches while preserving
# tracked PDF sources such as the guide manifest, filters, and template.
pdf-clean:
	$(PDF_BUILDER) \
		--clean

# Convenience target for running a local preview server from /docs.
serve: deps ensure-doc-stubs ensure-hugo-runtime
	$(HUGO_RUN_SERVER) server --bind 0.0.0.0 --disableFastRender --poll 700ms

# Prepare the docs tree for local browser automation by installing the
# Playwright CLI package and a local Firefox browser payload. Browser
# installation uses Playwright's installer because `playwright-cli
# install-browser` is not reliable in this environment. This target is
# optional and is not part of the normal docs build flow.
setup: npm-install
	$(NPM) exec playwright install firefox

# Remove every generated docs artifact, including PDF outputs, dependency
# caches, and browser automation downloads, so /docs returns to a source-only
# state.
mrproper: clean
	rm -rf .cache .npm-cache .playwright-browsers .tmp-home node_modules
