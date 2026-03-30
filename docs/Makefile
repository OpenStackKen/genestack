SHELL := /bin/bash

# Keep every docs-specific cache and download inside /docs so `mrproper`
# can return the tree to a source-only state without touching user-global
# tool state.
HOST_HOME := $(HOME)
export HOME := $(CURDIR)/.tmp-home
export XDG_CACHE_HOME := $(CURDIR)/.cache
export NPM_CONFIG_CACHE := $(CURDIR)/.npm-cache
export npm_config_cache := $(NPM_CONFIG_CACHE)
export PLAYWRIGHT_BROWSERS_PATH := $(CURDIR)/.playwright-browsers
export PATH := $(CURDIR)/node_modules/.bin:$(PATH)

HUGO ?= hugo
NPM ?= npm
NPX ?= npx
DOCKER ?= docker
BUILD_SENTINEL := public/build.txt
DOCS_BUILD_IMAGE ?= genestack-docs-build:local
DOCS_CONTAINER_RUNNER := ./scripts/run-build-container.sh
DOCS_CONTAINER_STAMP := .cache/docs-build-image.stamp

.PHONY: \
	build \
	clean \
	container \
	container-build \
	container-clean \
	container-deps \
	container-generate-release-notes \
	container-lint \
	container-run \
	container-shell \
	deps \
	lint \
	mrproper \
	serve \
	setup

# Build the static site from the Hugo root in /docs, then atomically write a
# simple post-build sentinel that can be polled at `/build.txt`.
build:
	$(HUGO)
	@mkdir -p public
	@tmp_file="$$(mktemp public/.build.txt.XXXXXX)"; \
	printf 'build_time_utc=%s\nbuild_epoch=%s\n' \
	  "$$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
	  "$$(date -u +%s)" > "$$tmp_file"; \
	mv "$$tmp_file" $(BUILD_SENTINEL)

# Hugo does not provide a standalone `clean` subcommand for site output.
# This target removes only the files Hugo generates for a local build.
clean:
	rm -rf public resources .hugo_build.lock

# Download everything required to build locally: Node-based asset tooling
# and Hugo module dependencies.
deps:
	$(NPM) install
	$(HUGO) mod tidy

# Convenience target for validating the shared Markdown sources in
# /docs/content using the docs-local markdownlint configuration.
lint:
	$(NPM) exec markdownlint-cli2 "content/**/*.md"

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
	rm -rf .cache .npm-cache .playwright-browsers .tmp-home node_modules

# Build the standalone docs tool image. This is separate from the local serving
# container and is intended to encapsulate Hugo, Node, Go, Python, reno, and
# pandoc for reproducible local and CI builds.
container: $(DOCS_CONTAINER_STAMP)

$(DOCS_CONTAINER_STAMP): Makefile Dockerfile docs-requirements.txt ../dev-requirements.txt
	@mkdir -p $(dir $(DOCS_CONTAINER_STAMP))
	HOME=$(HOST_HOME) $(DOCKER) buildx build --load -f Dockerfile -t $(DOCS_BUILD_IMAGE) ..
	@touch $(DOCS_CONTAINER_STAMP)

# Remove the locally built docs tool image and its stamp file so the next
# containerized docs command rebuilds the image from scratch.
container-clean:
	-HOME=$(HOST_HOME) $(DOCKER) image rm -f $(DOCS_BUILD_IMAGE)
	rm -f $(DOCS_CONTAINER_STAMP)

# Run the host-native dependency bootstrap inside the dedicated docs build
# image. The wrapper mounts the repo and all cache locations under /docs.
container-deps: container
	HOME=$(HOST_HOME) DOCS_BUILD_IMAGE=$(DOCS_BUILD_IMAGE) $(DOCS_CONTAINER_RUNNER) bash -c 'npm install && hugo mod tidy'

# Run markdownlint in the containerized docs build environment.
container-lint: container
	HOME=$(HOST_HOME) DOCS_BUILD_IMAGE=$(DOCS_BUILD_IMAGE) $(DOCS_CONTAINER_RUNNER) bash -c 'npm exec markdownlint-cli2 "content/**/*.md"'

# Build the Hugo site inside the docs build container and write the same
# post-build sentinel used by the host-native build path.
container-build: container
	HOME=$(HOST_HOME) DOCS_BUILD_IMAGE=$(DOCS_BUILD_IMAGE) $(DOCS_CONTAINER_RUNNER) bash -c '\
	  hugo && \
	  mkdir -p public && \
	  tmp_file="$$(mktemp public/.build.txt.XXXXXX)" && \
	  printf "build_time_utc=%s\nbuild_epoch=%s\n" \
	    "$$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
	    "$$(date -u +%s)" > "$$tmp_file" && \
	  mv "$$tmp_file" $(BUILD_SENTINEL)'

# Generate the Hugo-ready release-notes page inside the docs build container.
# The underlying reno invocation must run from the repo root, so the helper
# script handles that path transition explicitly.
container-generate-release-notes: container
	HOME=$(HOST_HOME) DOCS_BUILD_IMAGE=$(DOCS_BUILD_IMAGE) $(DOCS_CONTAINER_RUNNER) bash -c './scripts/generate-release-notes.sh'

# Run an arbitrary command inside the docs build container. Example:
# make container-run CMD='python3 ../scripts/generate_product_matrix.py'
container-run: container
	@test -n "$(CMD)" || { echo 'Set CMD, for example: make container-run CMD='\''hugo version'\''' >&2; exit 1; }
	HOME=$(HOST_HOME) DOCS_BUILD_IMAGE=$(DOCS_BUILD_IMAGE) $(DOCS_CONTAINER_RUNNER) bash -c '$(CMD)'

# Drop into an interactive shell inside the docs build container.
container-shell: container
	HOME=$(HOST_HOME) DOCS_BUILD_IMAGE=$(DOCS_BUILD_IMAGE) DOCS_CONTAINER_INTERACTIVE=1 $(DOCS_CONTAINER_RUNNER) bash
