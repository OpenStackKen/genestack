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

.PHONY: build clean deps lint mrproper serve setup

# Build the static site from the Hugo root in /docs.
build:
	$(HUGO)

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

# Prepare the docs tree for agent-driven browser work by installing the
# Playwright MCP package and a local Chromium browser payload.
setup: deps
	$(NPM) exec playwright install chromium

# Remove every generated docs artifact, including dependency caches and
# browser automation downloads, so /docs returns to a source-only state.
mrproper: clean
	rm -rf .cache .npm-cache .playwright-browsers .tmp-home node_modules
