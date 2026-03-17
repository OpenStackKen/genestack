---
title: "Working on docs locally"
weight: 10
aliases:
  - /mkdocs-howto/
---
Use the Hugo site rooted at `/docs` to preview documentation changes locally.

Install the docs tooling dependencies from the `/docs` tree:

```shell
cd docs
make deps
```

> [!TIP]
>
> The Makefile keeps all docs-local caches, browser downloads, and Node
> tooling inside `/docs`, so `make mrproper` can restore the tree to a
> source-only state.

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

Lint the shared Markdown sources:

```shell
cd docs
make lint
```

Prepare Playwright MCP and the browser payload used for agent-based docs
development:

```shell
cd docs
make setup
```

Remove build output, local dependency downloads, and agent-development
artifacts:

```shell
cd docs
make mrproper
```
