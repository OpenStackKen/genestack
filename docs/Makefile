SHELL := /bin/bash

# Keep every docs-specific cache and download inside /docs so `mrproper`
# can return the tree to a source-only state without touching user-global
# tool state.
export XDG_CACHE_HOME := $(CURDIR)/.cache
export HUGO_CACHEDIR := $(CURDIR)/.cache/hugo_cache
export NPM_CONFIG_CACHE := $(CURDIR)/.npm-cache
export npm_config_cache := $(NPM_CONFIG_CACHE)
export PLAYWRIGHT_BROWSERS_PATH := $(CURDIR)/.playwright-browsers
export PATH := $(CURDIR)/node_modules/.bin:$(PATH)

HUGO ?= hugo
NPM ?= npm
NPX ?= npx
PYTHON ?= python3
BUILD_SENTINEL := public/build.txt
PRODUCT_MATRIX_PAGE := content/overview/product-matrix.md
PRODUCT_MATRIX_STUB := scripts/product-matrix.stub.md
PDF_BUILDER := scripts/mkpdf.sh
PDF_PANDOC_IMAGE := $(shell $(PYTHON) -c 'import pathlib, tomllib; print(tomllib.loads(pathlib.Path("pdf.toml").read_text(encoding="utf-8"))["pandoc_image"])')
PDF_PANDOC_DOCKERFILE := $(shell $(PYTHON) -c 'import pathlib, tomllib; print(tomllib.loads(pathlib.Path("pdf.toml").read_text(encoding="utf-8"))["pandoc_dockerfile"])')
PDF_PANDOC_CONTEXT := $(dir $(PDF_PANDOC_DOCKERFILE))
PDF_PANDOC_IMAGE_STAMP := .cache/pdf-pandoc-image.stamp
NPM_INSTALL_STAMP := node_modules/.install-stamp
HUGO_MOD_TIDY_STAMP := .cache/hugo-mod-tidy.stamp
.DEFAULT_GOAL := build

.PHONY: container npm-install hugo-mod-tidy deps build clean ensure-doc-stubs lint mrproper pdf pdf-clean serve setup

# Download everything required to build locally: Node-based asset tooling,
# Hugo module dependencies, and the repo-owned Pandoc image used by the PDF
# wrapper. The image build is split into its own file-backed target so Make can
# compare the cached build artifact against the Dockerfile and skip the rebuild
# path when nothing relevant changed.
deps: container npm-install hugo-mod-tidy

# Human-friendly alias for the file-backed Pandoc image build artifact.
container: $(PDF_PANDOC_IMAGE_STAMP)
	@if ! docker image inspect $(PDF_PANDOC_IMAGE) >/dev/null 2>&1; then \
		rm -f $(PDF_PANDOC_IMAGE_STAMP); \
		$(MAKE) $(PDF_PANDOC_IMAGE_STAMP); \
	fi

# Human-friendly alias for the Node dependency install artifact.
npm-install: $(NPM_INSTALL_STAMP)

# Human-friendly alias for the Hugo module tidy artifact.
hugo-mod-tidy: $(HUGO_MOD_TIDY_STAMP)

# The stamp records that the local Pandoc image was built from the current
# Dockerfile/config inputs. When this target is newer than those inputs, `make`
# can skip `docker build` entirely for normal docs and PDF runs.
$(PDF_PANDOC_IMAGE_STAMP): $(PDF_PANDOC_DOCKERFILE) pdf.toml
	@mkdir -p $(dir $@)
	docker build --tag $(PDF_PANDOC_IMAGE) --file $(PDF_PANDOC_DOCKERFILE) $(PDF_PANDOC_CONTEXT)
	@touch $@

# Record that `npm install` has been applied to the current package manifest.
# Keeping the stamp inside `node_modules/` means removing that directory also
# removes the install marker, so Make will correctly reinstall on the next run.
$(NPM_INSTALL_STAMP): package.json package-lock.json
	$(NPM) install
	@mkdir -p $(dir $@)
	@touch $@

# Record that Hugo module dependencies have been reconciled against the current
# Hugo/module manifests. The stamp lives in `.cache/` because the command's
# durable outputs are the checked-in Go module files plus the Hugo module cache.
$(HUGO_MOD_TIDY_STAMP): hugo.toml go.mod go.sum
	@mkdir -p $(dir $@)
	$(HUGO) mod tidy
	@touch $@

# Restore tracked docs stubs when generated pages are absent.
ensure-doc-stubs:
	@test -f $(PRODUCT_MATRIX_PAGE) || cp $(PRODUCT_MATRIX_STUB) $(PRODUCT_MATRIX_PAGE)

# Build the static site from the Hugo root in /docs, then atomically write a
# simple post-build sentinel that can be polled at `/build.txt`.
build: deps ensure-doc-stubs
	$(HUGO)
	@mkdir -p public
	@tmp_file="$$(mktemp public/.build.txt.XXXXXX)"; \
	printf 'build_time_utc=%s\nbuild_epoch=%s\n' \
	  "$$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
	  "$$(date -u +%s)" > "$$tmp_file"; \
	mv "$$tmp_file" $(BUILD_SENTINEL)

# Hugo does not provide a standalone `clean` subcommand for site output.
# This target removes local build output and restores generated docs pages
# back to their checked-in stub form.
clean:
	rm -rf public resources .hugo_build.lock
	cp $(PRODUCT_MATRIX_STUB) $(PRODUCT_MATRIX_PAGE)

# Convenience target for validating the shared Markdown sources in
# /docs/content using the docs markdownlint configuration.
lint:
	$(NPM) exec markdownlint-cli2 "content/**/*.md"

# Build every configured guide PDF. The Python assembler writes unified
# Markdown build artifacts and the shell wrapper runs the Pandoc container
# against those generated inputs.
pdf: deps ensure-doc-stubs
	$(PDF_BUILDER) all

# Remove only generated PDF artifacts and scratch caches while preserving
# tracked PDF sources such as the guide manifest, filters, and template.
pdf-clean:
	$(PDF_BUILDER) \
		--clean

# Convenience target for running a local preview server from /docs.
serve:
	$(HUGO) server --disableFastRender

# Prepare the docs tree for local browser automation by installing the
# Playwright CLI package and a local Firefox browser payload. Browser
# installation uses Playwright's installer because `playwright-cli
# install-browser` is not reliable in this environment.
setup: deps
	$(NPM) exec playwright install firefox

# Remove every generated docs artifact, including dependency caches and
# browser automation downloads, so /docs returns to a source-only state.
mrproper: clean
	rm -rf .cache .npm-cache .playwright-browsers node_modules
