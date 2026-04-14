---
title: "Working on docs locally"
weight: 10
---
Use the Hugo site rooted at `/docs` to preview documentation changes locally.
Docker is required for local site builds and previews. A host Hugo install is
not part of the supported workflow.

Install the docs tooling dependencies from the `/docs` tree:

```shell
cd docs
make deps
```

> [!TIP]
>
> The Makefile keeps the Hugo container cache, docs-local caches, browser
> downloads, and Node tooling inside `/docs`, so `make mrproper` can restore
> the tree to a source-only state.

Start the local docs server:

```shell
cd docs
make serve
```

Build the local docs site without starting a server:

```shell
cd docs
make build
```

When maintainers need to reconcile Hugo modules explicitly:

```shell
cd docs
make hugo-mod-tidy
```

Lint the shared Markdown sources:

```shell
cd docs
make lint
```

Prepare the local Playwright CLI package and Firefox browser payload used for
docs automation:

```shell
cd docs
make setup
```

> [!NOTE]
>
> This repository now treats browser automation as Playwright CLI work, not
> MCP server setup. `make setup` installs the local `playwright-cli` package
> and Firefox browser payload only.

Use the local CLI through npm exec:

```shell
cd docs
npm exec -- playwright-cli --help
```

Install the Firefox browser payload:

```shell
cd docs
npm exec playwright install firefox
```

Remove build output, local dependency downloads, and agent-development
artifacts:

```shell
cd docs
make mrproper
```
