# Docs Refactor Plan

## Summary

Replace the MkDocs Material docs stack with a local Hugo site that uses the
default Docsy theme while treating `/docs/content` as the canonical shared
content tree inside a single `/docs` Hugo site root for both this repository
and `genestack-site`.

## Implemented Direction

- `/docs` is the Hugo site root.
- `/docs/content` is the shared source of truth for Markdown, front matter, and
  content assets.
- Shared content is reorganized into section directories under `/docs/content`.
- MkDocs-specific admonitions are migrated to GFM alerts.
- `markdownlint` is the source-format compliance tool for `/docs/content`.
- Internal renderer and contract notes live under `/docs/content/info`.

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
- Document any renderer-specific expectations in `/docs/content/info`.
