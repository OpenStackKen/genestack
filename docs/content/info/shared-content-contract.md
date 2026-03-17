---
title: "Shared Content Contract"
weight: 10
---
The `/docs/content` tree is the canonical shared source for Genestack
documentation. The surrounding `/docs` directory is the local Hugo site root.
Both the local Hugo site in this repository and downstream sites such as
`genestack-site` should consume the same content structure.

## Source Rules

- Keep shared documentation content in Markdown files under `/docs/content`.
- Keep shared documentation images and supporting assets under
  `/docs/content/assets`.
- Use front matter for titles, ordering, aliases, and other portable metadata.
- Prefer GFM-compatible Markdown in page bodies.
- Use GFM alert blocks instead of MkDocs `!!!` admonitions.
- Keep renderer-specific assumptions out of page bodies when a neutral Markdown
  form is available.

## Rendering Rules

- The local Hugo site is responsible for theme selection, module imports, and
  renderer implementation details.
- `genestack-site` should consume the shared content tree without depending on
  the local Hugo mechanism in this repository.
- If a renderer needs nonstandard support for shared content, document that
  behavior here before depending on it.

## Stable Paths

- Shared content paths are authoritative.
- Internal links should use site-root-relative paths so both local and
  downstream sites inherit the same structure.
- Shared assets should use `/assets/...` paths.
