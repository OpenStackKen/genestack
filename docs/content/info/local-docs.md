---
title: "Working on docs locally"
weight: 10
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

Prepare the local Playwright package and Firefox browser payload used for docs
automation:

```shell
cd docs
make setup
```

> [!NOTE]
>
> Codex MCP server names are configured outside this repository in the local
> Codex config. In this environment the browser-specific server names are
> `playwright_firefox`, `playwright_chrome`, and `playwright_webkit`, with
> Firefox preferred by default. `make setup` prepares the local package and
> browser payload only; it does not define or rename MCP servers.

Remove build output, local dependency downloads, and agent-development
artifacts:

```shell
cd docs
make mrproper
```
