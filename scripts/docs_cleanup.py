#!/usr/bin/env python3

from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "content"

ALERT_MAP = {
    "note": "NOTE",
    "info": "NOTE",
    "abstract": "NOTE",
    "example": "IMPORTANT",
    "genestack": "IMPORTANT",
    "banner": "IMPORTANT",
    "tip": "TIP",
    "success": "TIP",
    "warning": "WARNING",
    "caution": "CAUTION",
}


def deindent(lines: list[str]) -> list[str]:
    output = []
    for line in lines:
        if line.startswith("    "):
            output.append(line[4:])
        elif line.startswith("\t"):
            output.append(line[1:])
        else:
            output.append(line)
    return output


def format_alert(kind: str, title: str | None, block_lines: list[str]) -> str:
    out = [f"> [!{kind}]\n"]
    if title:
        out.append(f"> **{title}**\n")
    if block_lines:
        out.append(">\n")
    for entry in block_lines:
        out.append(">\n" if entry.strip() == "" else f"> {entry}")
    if not out[-1].endswith("\n\n"):
        out.append("\n")
    return "".join(out)


def language_for(path: Path) -> str:
    return {
        ".sh": "shell",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".xml": "xml",
    }.get(path.suffix, "text")


def expand_snippets(content: str) -> str:
    out: list[str] = []
    for line in content.splitlines(keepends=True):
        match = re.match(r'^(\s*> ?\s*|\s*)--8<--\s+"([^"]+)"\s*$', line)
        if not match:
            out.append(line)
            continue
        prefix, include_name = match.groups()
        include_path = ROOT / include_name
        if not include_path.is_file():
            out.append(line)
            continue
        out.append(f"{prefix}```{language_for(include_path)}\n")
        for included in include_path.read_text().splitlines(keepends=True):
            out.append(f"{prefix}{included}")
        out.append(f"{prefix}```\n")
    return "".join(out)


def convert_blocks(content: str) -> str:
    lines = content.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        bang = re.match(r'^!!!\s+([A-Za-z]+)(?:\s+"([^"]+)")?\s*$', line)
        fold = re.match(r'^\?\?\?(?:\+\+)?(?:\s+([A-Za-z]+))?(?:\s+"([^"]+)")?\s*$', line)
        inline = re.match(r'^!!!\s+([A-Za-z]+)\s+(.+?)\s*$', line)
        if bang or fold:
            match = bang or fold
            kind = ALERT_MAP.get((match.group(1) or "note").lower(), "NOTE")
            title = match.group(2)
            i += 1
            block: list[str] = []
            while i < len(lines):
                current = lines[i]
                if not (current.strip() == "" or current.startswith("    ") or current.startswith("\t")):
                    break
                block.append(current)
                i += 1
            out.append(format_alert(kind, title, deindent(block)))
            continue
        if inline:
            kind = ALERT_MAP.get(inline.group(1).lower(), "NOTE")
            out.append(format_alert(kind, None, [inline.group(2) + "\n"]))
            i += 1
            continue
        out.append(line)
        i += 1
    return "".join(out)


def permalink_for(path: Path) -> str:
    relative = str(path.relative_to(DOCS))
    if relative == "_index.md":
        return "/"
    if relative.endswith("/_index.md"):
        return f"/{re.sub(r'/_index\.md$', '/', relative)}"
    return f"/{re.sub(r'\.md$', '/', relative)}"


def build_page_map() -> dict[str, str]:
    return {path.name: permalink_for(path) for path in DOCS.rglob("*.md")}


def rewrite_links(content: str, page_map: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        raw = match.group(1)
        if re.match(r"^[a-z]+://", raw, flags=re.IGNORECASE):
            return f"({raw})"
        parts = raw.split("#", 1)
        page = parts[0]
        anchor = parts[1] if len(parts) == 2 else None
        target = page_map.get(os.path.basename(page))
        if not target:
            return f"({raw})"
        return f"({target}#{anchor})" if anchor else f"({target})"

    return re.sub(r"\(([^)]+?\.md(?:#[^)]+)?)\)", repl, content)


def main() -> None:
    page_map = build_page_map()
    for path in DOCS.rglob("*.md"):
        content = path.read_text()
        content = convert_blocks(content)
        content = expand_snippets(content)
        content = re.sub(r"\]\(([^)]+)\)\{[^}\n]*\}", r"](\1)", content)
        content = rewrite_links(content, page_map)
        path.write_text(content)


if __name__ == "__main__":
    main()
