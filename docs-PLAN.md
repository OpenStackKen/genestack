# Docs Refactor Plan

## Summary

Replace the MkDocs Material docs stack with a local Hugo site that uses the
default Docsy theme while treating `/docs` as the canonical shared content tree
for both this repository and `genestack-site`.

## Implemented Direction

- `/docs` is the shared source of truth for Markdown, front matter, and assets.
- The local Hugo mechanism lives in `/local-docs`.
- Shared content is reorganized into section directories under `/docs`.
- MkDocs-specific admonitions are migrated to GFM alerts.
- `markdownlint` is the source-format compliance tool for `/docs`.
- Internal renderer and contract notes live under `/docs/info`.

## Workflow

- Active branch: `codex/docs-refactor`
- Matching fork branch to maintain: `openstackken/docs-refactor`
- Delivery target: PR from `openstackken/genestack` to `rackerlabs/genestack`
- Upstream drift handling: periodically compare `openstackken/main` to
  `rackerlabs/main`, resync main, then refresh the refactor branch as needed

## Shared Content Contract

- Keep content in Markdown and shared assets only.
- Use front matter for ordering, titles, and aliases.
- Keep source Markdown as close to GFM as practical.
- Document any renderer-specific expectations in `/docs/info`.
