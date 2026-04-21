---
title: "PDF Rendering Test"
debug: true
---

This page exists to test how inline code such as `pip`, `clouds.yaml`,
`--help`, `C:\Python27\Scripts`, and `#` renders in the PDF pipeline.

## Body Text

Inline code in ordinary prose should look balanced next to the surrounding text.
This sentence includes `pip`, `clouds.yaml`, `--debug`, `#`, `##`, and
`C:\Python27\Scripts`.

## Heading with `pip`

This heading uses `pip` so we can inspect inline code inside the heading itself.

### Subheading with `clouds.yaml`

This subheading checks a filename-style inline code span inside a smaller
heading context.

#### Nested Heading with `--help`

This nested heading checks a flag-style inline code span.

## Lists with `inline`

- Bullet item with `pip`.
- Bullet item with `C:\Python27\Scripts`.
- Bullet item with `#` and `##`.

1. Numbered item with `clouds.yaml`.
2. Numbered item with `--help`.

## Callout with `inline`

> [!NOTE] `pip` in a title:
>
> The body of this callout includes `pip`, `clouds.yaml`, and
> `C:\Python27\Scripts`.

## Table with `inline`

| Context | Example |
| ------- | ------- |
| Filename | `clouds.yaml` |
| Flag | `--help` |
| Windows path | `C:\Python27\Scripts` |
| Heading marker | `#` |

## Paragraph with `GENESTACK`

The custom `GENESTACK` token is useful here because it is short, visually
distinct, and easy to compare against the surrounding heading font.
