---
title: "Local Hugo Components"
weight: 30
---

# Local Hugo Components

The local docs site uses Hugo modules at the `/docs` site root so the shared
content tree under `/docs/content` stays mechanism-light.

## Required Local Components

- Docsy provides the local documentation theme.
- `martignoni/hugo-notice` is available to support notice rendering and future
  notice-compatible theme behavior in the local site.

## Component Policy

- Prefer existing Hugo modules before adding custom local templates.
- Keep those modules and any renderer-specific templates at the Hugo site root,
  not in `/docs/content`.
- If a shared content feature depends on local renderer support, document that
  dependency in this directory.
