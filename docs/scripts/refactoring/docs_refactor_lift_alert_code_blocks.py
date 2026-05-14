#!/usr/bin/env python3
"""Lift fenced code blocks out of GFM alert blockquotes.

This helper is intentionally narrow. It rewrites Markdown alert blocks that
look like:

> [!IMPORTANT]
> Alert text
>
> ```shell
> echo hi
> ```

into:

> [!IMPORTANT]
> Alert text

```shell
echo hi
```

If an alert has prose both before and after a lifted code block, the prose is
preserved by splitting the original alert into multiple alert blocks around the
standalone code fence. That keeps the content order stable while ensuring code
is no longer nested inside the alert.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ALERT_START_RE = re.compile(r"^> \[![^\]]+\]")
ALERT_HEADER_RE = re.compile(r"^(> \[![^\]]+\])(?:[ \t]+(.*))?$")
FENCE_RE = re.compile(r"^(```+|~~~+)")


@dataclass(frozen=True)
class RewriteStats:
    """One file-level rewrite summary."""

    path: Path
    changed: bool
    alert_blocks_rewritten: int
    code_blocks_lifted: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Markdown files or directories to process")
    parser.add_argument("--write", action="store_true", help="Write changes back to disk")
    return parser.parse_args()


def iter_markdown_files(raw_paths: Iterable[str]) -> list[Path]:
    files: list[Path] = []
    for raw_path in raw_paths:
        path = Path(raw_path)
        if path.is_dir():
            files.extend(sorted(candidate for candidate in path.rglob("*.md") if candidate.is_file()))
        elif path.is_file():
            files.append(path)
        else:
            raise SystemExit(f"path not found: {path}")
    # Preserve deterministic order while de-duplicating repeated arguments.
    return list(dict.fromkeys(path.resolve() for path in files))


def unquote_alert_line(line: str) -> str:
    """Remove the leading blockquote marker from one alert line."""

    if not line.startswith(">"):
        raise ValueError(f"alert line does not start with '>': {line!r}")
    content = line[1:]
    if content.startswith(" "):
        content = content[1:]
    return content


def quote_alert_lines(lines: Iterable[str]) -> list[str]:
    """Reapply a blockquote marker to alert body content."""

    quoted: list[str] = []
    for line in lines:
        quoted.append(f"> {line}" if line else ">")
    return quoted


def trim_blank_lines(lines: list[str]) -> list[str]:
    """Drop leading/trailing blank lines from a text segment.

    The source alerts frequently include extra quoted blank lines before a code
    fence. Once the fence is lifted out, keeping those outer blank lines only
    produces loose empty alert paragraphs, so the migration trims them while
    leaving interior blank lines untouched.
    """

    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def normalize_alert_code_fences(lines: list[str]) -> list[str]:
    """Repair a couple of recurring malformed quoted-fence patterns.

    Some pages contain duplicate consecutive closing fences after a code block.
    Others end an alert immediately after code content without repeating the
    closing fence. Both patterns are mechanical authoring mistakes, and fixing
    them here lets the alert-lifting rewrite stay deterministic across the repo.
    """

    normalized: list[str] = []
    in_code = False
    fence_char = ""

    for line in lines:
        fence_match = FENCE_RE.match(line)
        if not fence_match:
            normalized.append(line)
            continue

        current_char = fence_match.group(1)[0]
        if in_code:
            if current_char == fence_char:
                if normalized and normalized[-1] == line:
                    continue
                normalized.append(line)
                in_code = False
                fence_char = ""
                continue
            normalized.append(line)
            continue

        normalized.append(line)
        in_code = True
        fence_char = current_char

    if in_code:
        normalized.append(fence_char * 3)

    return normalized


def rewrite_alert_block(lines: list[str]) -> tuple[list[str], int]:
    """Lift quoted fenced code blocks out of one alert block.

    Returns the rewritten lines plus the number of fenced code blocks lifted.
    If the alert contains an unterminated quoted fence, the block is returned
    unchanged so the script stays conservative in malformed input.
    """

    header_match = ALERT_HEADER_RE.match(lines[0])
    if not header_match:
        return lines, 0
    alert_marker = header_match.group(1)
    inline_title = (header_match.group(2) or "").strip()

    body_lines = normalize_alert_code_fences([unquote_alert_line(line) for line in lines[1:]])
    segments: list[tuple[str, list[str]]] = []
    current_text: list[str] = [inline_title] if inline_title else []
    current_code: list[str] = []
    in_code = False
    fence_char = ""
    code_blocks_lifted = 0

    for line in body_lines:
        fence_match = FENCE_RE.match(line)
        if in_code:
            current_code.append(line)
            if fence_match and fence_match.group(1)[0] == fence_char:
                segments.append(("code", current_code))
                current_code = []
                in_code = False
                fence_char = ""
                code_blocks_lifted += 1
            continue

        if fence_match:
            if current_text:
                segments.append(("text", current_text))
                current_text = []
            current_code = [line]
            in_code = True
            fence_char = fence_match.group(1)[0]
            continue

        current_text.append(line)

    if in_code:
        return lines, 0

    if current_text:
        segments.append(("text", current_text))

    if code_blocks_lifted == 0:
        return lines, 0

    rewritten: list[str] = []
    first_text_segment = True
    for kind, segment_lines in segments:
        if kind == "text":
            trimmed_text = trim_blank_lines(segment_lines)
            if not trimmed_text:
                continue
            if rewritten and rewritten[-1] != "":
                rewritten.append("")
            if first_text_segment and inline_title:
                rewritten.append(f"{alert_marker} {trimmed_text[0]}")
                rewritten.extend(quote_alert_lines(trimmed_text[1:]))
            else:
                rewritten.append(alert_marker)
                rewritten.extend(quote_alert_lines(trimmed_text))
            first_text_segment = False
            continue

        if rewritten and rewritten[-1] != "":
            rewritten.append("")
        rewritten.extend(segment_lines)

    return rewritten, code_blocks_lifted


def rewrite_file(path: Path, *, write: bool) -> RewriteStats:
    original_text = path.read_text(encoding="utf-8")
    had_trailing_newline = original_text.endswith("\n")
    lines = original_text.splitlines()
    rewritten: list[str] = []
    alert_blocks_rewritten = 0
    code_blocks_lifted = 0

    index = 0
    while index < len(lines):
        if not ALERT_START_RE.match(lines[index]):
            rewritten.append(lines[index])
            index += 1
            continue

        alert_lines = [lines[index]]
        index += 1
        while index < len(lines) and lines[index].startswith(">"):
            alert_lines.append(lines[index])
            index += 1

        rewritten_block, lifted = rewrite_alert_block(alert_lines)
        if lifted:
            alert_blocks_rewritten += 1
            code_blocks_lifted += lifted
        rewritten.extend(rewritten_block)

    rewritten_text = "\n".join(rewritten)
    if had_trailing_newline:
        rewritten_text += "\n"

    changed = rewritten_text != original_text
    if write and changed:
        path.write_text(rewritten_text, encoding="utf-8")

    return RewriteStats(
        path=path,
        changed=changed,
        alert_blocks_rewritten=alert_blocks_rewritten,
        code_blocks_lifted=code_blocks_lifted,
    )


def main() -> int:
    args = parse_args()
    files = iter_markdown_files(args.paths)
    stats = [rewrite_file(path, write=args.write) for path in files]

    changed_files = 0
    rewritten_alerts = 0
    lifted_blocks = 0
    for item in stats:
        if not item.changed:
            continue
        changed_files += 1
        rewritten_alerts += item.alert_blocks_rewritten
        lifted_blocks += item.code_blocks_lifted
        action = "rewrote" if args.write else "would rewrite"
        print(
            f"[lift-alert-code] {action}: {item.path} "
            f"(alerts={item.alert_blocks_rewritten}, code_blocks={item.code_blocks_lifted})"
        )

    print(
        f"[lift-alert-code] summary: files={changed_files} "
        f"alerts={rewritten_alerts} code_blocks={lifted_blocks}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
