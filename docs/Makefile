SHELL := /bin/bash

# Keep every docs-specific cache and download inside /docs so `mrproper`
# can return the tree to a source-only state without touching user-global
# tool state.
export HOME := $(CURDIR)/.tmp-home
export XDG_CACHE_HOME := $(CURDIR)/.cache
export NPM_CONFIG_CACHE := $(CURDIR)/.npm-cache
export npm_config_cache := $(NPM_CONFIG_CACHE)
export PLAYWRIGHT_BROWSERS_PATH := $(CURDIR)/.playwright-browsers
export PATH := $(CURDIR)/node_modules/.bin:$(PATH)

HUGO ?= hugo
NPM ?= npm
NPX ?= npx
BUILD_SENTINEL := public/build.txt

.PHONY: build clean deps lint mrproper serve setup

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
# Playwright package and a local Firefox browser payload. Codex MCP server
# names such as `playwright_firefox` are configured outside this repo.
setup: deps
	$(NPM) exec playwright install firefox

# Remove every generated docs artifact, including dependency caches and
# browser automation downloads, so /docs returns to a source-only state.
mrproper: clean
	rm -rf .cache .npm-cache .playwright-browsers .tmp-home node_modules
