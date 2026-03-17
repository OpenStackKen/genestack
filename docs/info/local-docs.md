---
title: "Working on docs locally"
weight: 10
aliases:
  - /mkdocs-howto/
---

# Working on docs locally

Use the Hugo site in `/local-docs` to preview documentation changes locally.

Install the docs tooling dependencies from the repository root:

```shell
npm install
(cd local-docs && hugo mod tidy)
```

> [!TIP]
>
> Hugo module downloads happen from the `local-docs` site configuration, while
> markdownlint runs from the repository root.

Start the local docs server:

```shell
npm run docs:serve
```

Build the local docs site without starting a server:

```shell
npm run docs:build
```

Lint the shared Markdown sources:

```shell
npm run docs:lint
```
