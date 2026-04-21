Refactoring helpers for `docs/`.

This directory is intentionally separate from the build pipeline entrypoints in
`/docs/scripts`.

Use the scripts here for content migration, cleanup, restructuring, and other
one-off or batch refactoring tasks. Use `/docs/scripts/mkpdf.sh`,
`/docs/scripts/assemble-markdown.py`, and other top-level script entrypoints
for the active documentation build pipeline.

Current refactoring helpers:

- `docs_refactor_cleanup.py`
- `docs_refactor_content.py`
- `docs_refactor_docsy_normalize.py`
- `docs_refactor_docsy_restructure.py`
- `docs_refactor_lift_alert_code_blocks.py`
