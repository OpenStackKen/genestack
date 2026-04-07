Refactoring helpers for `docs/`.

This directory is intentionally separate from the build pipeline entrypoints in
`/docs/scripts`.

Use the scripts here for content migration, cleanup, restructuring, and other
one-off or batch refactoring tasks. Use `/docs/scripts/mkpdf.sh`,
`/docs/scripts/assemble-markdown.py`, and other top-level script entrypoints
for the active documentation build pipeline.
