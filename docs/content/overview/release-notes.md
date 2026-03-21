---
title: "Release Notes"
weight: 50
---
All release notes are generated using [reno](https://docs.openstack.org/reno/latest/).

The containerized docs tooling already carries the required Python
dependencies, `reno`, and `pandoc`.

To manually regenerate this page from the repo using the current docs tool
image, run the following command from `genestack/docs`:

```bash
make container-generate-release-notes
```

> [!info]
>
> Under the hood, the release notes generator:
>
> - changes to the repo root so `reno` can read the release-notes config and notes
> - writes the intermediate ReStructuredText document to a temporary file
> - converts that RST to Markdown with `pandoc`
> - writes the final page to `/docs/content/overview/release-notes.md`
