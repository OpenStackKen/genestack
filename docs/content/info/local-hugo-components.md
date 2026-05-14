---
title: "Local Hugo Components"
weight: 30
---
The local docs site uses Hugo modules at the `/docs` site root so the shared
content tree under `/docs/content` stays mechanism-light.

## Required Local Components

- Docsy provides the local documentation theme.
- GFM alert callouts are rendered by Docsy's built-in Markdown alert styling.

## Component Policy

- Prefer existing Hugo modules before adding custom local templates.
- Keep those modules and any renderer-specific templates at the Hugo site root,
  not in `/docs/content`.
- If a shared content feature depends on local renderer support, document that
  dependency in this directory.
