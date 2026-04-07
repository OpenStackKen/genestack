#!/usr/bin/env python3

from __future__ import annotations

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


def split_front_matter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    parts = re.split(r"^---\s*$\n", text, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3 or parts[0] != "":
        return "", text
    return f"---\n{parts[1]}---\n", parts[2]


def clean_title(value: str) -> str:
    # Source titles should be semantic text, not presentational HTML.
    return re.sub(r"</?u>", "", value).strip()


def deindent(lines: list[str]) -> list[str]:
    output: list[str] = []
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


def convert_mkdocs_blocks(body: str) -> str:
    lines = body.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    in_fence = False
    while i < len(lines):
        line = lines[i]
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue
        if in_fence:
            out.append(line)
            i += 1
            continue

        bang = re.match(r'^(?:>\s*)*!!!\s+([A-Za-z]+)(?:\s+"([^"]+)")?\s*$', line)
        fold = re.match(r'^(?:>\s*)*\?\?\?(?:\+\+)?(?:\s+([A-Za-z]+))?(?:\s+"([^"]+)")?\s*$', line)
        inline = re.match(r'^(?:>\s*)*!!!\s+([A-Za-z]+)\s+(.+?)\s*$', line)
        if bang or fold:
            match = bang or fold
            kind = ALERT_MAP.get((match.group(1) or "note").lower(), "NOTE")
            title = match.group(2)
            i += 1
            block: list[str] = []
            while i < len(lines):
                current = lines[i]
                if re.match(r"^\s*```", current):
                    break
                if not (
                    current.strip() == ""
                    or current.startswith("    ")
                    or current.startswith("\t")
                    or current.startswith(">    ")
                    or current.startswith(">\t")
                    or re.match(r"^>\s*$", current)
                ):
                    break
                current = re.sub(r"^>\s?", "", current)
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


def convert_mkdocs_tabs(body: str) -> str:
    lines = body.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    in_fence = False
    while i < len(lines):
        line = lines[i]
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            out.append(line)
            i += 1
            continue
        if in_fence:
            out.append(line)
            i += 1
            continue

        match = re.match(r'^(?:>\s*)*===\s+"([^"]+)"\s*$', line)
        if not match:
            out.append(line)
            i += 1
            continue

        title = match.group(1)
        i += 1
        block: list[str] = []
        while i < len(lines):
            current = lines[i]
            if re.match(r"^\s*```", current):
                block.append(re.sub(r"^>\s?", "", current))
                i += 1
                while i < len(lines):
                    inner = lines[i]
                    block.append(re.sub(r"^>\s?", "", inner))
                    i += 1
                    if re.match(r"^\s*```", inner):
                        break
                continue
            if re.match(r'^(?:>\s*)*===\s+"', current):
                break
            if current.strip() and not current.startswith("    ") and not current.startswith("\t") and not current.startswith(">"):
                break
            block.append(re.sub(r"^>\s?", "", current))
            i += 1

        out.append(f"\n### {title}\n\n")
        out.extend(deindent(block))
        if out and not out[-1].endswith("\n\n"):
            out.append("\n")
    return "".join(out)


def normalize_alert_syntax(body: str) -> str:
    lines = body.splitlines(keepends=True)
    out: list[str] = []
    in_alert = False
    alert_has_body = False
    i = 0

    def is_alert_marker(value: str) -> bool:
        return bool(re.match(r"^(?:>\s*)?\[![A-Z]+\]\s*$", value))

    def is_quoted_line(value: str) -> bool:
        return value.startswith(">")

    while i < len(lines):
        line = lines[i]

        # Normalize stray non-quoted GFM alert markers into real alerts.
        if re.match(r"^\[![A-Z]+\]\s*$", line):
            line = f"> {line}"

        if in_alert and re.match(r"^>\s*\[![A-Z]+\]\s*$", line) and alert_has_body:
            out.append("\n")
            alert_has_body = False

        # Fix malformed alert lines where a closing code fence was appended to
        # the end of the content line.
        line = re.sub(r"^(> .*?)> ```\s*$", r"\1\n> ```\n", line)

        # Collapse duplicate quoted opening fences created by the first
        # conversion pass. Keep the first fence and drop the immediate duplicate.
        if re.match(r"^> ```", line) and i + 1 < len(lines) and re.match(r"^> ```", lines[i + 1]):
            next_line = lines[i + 1]
            if not re.match(r"^> ```\s*$", line) or re.match(r"^> ```\s*$", next_line):
                i += 1
            else:
                line = next_line
                i += 1

        # Collapse duplicate quoted closing fences.
        if re.match(r"^> ```\s*$", line) and i + 1 < len(lines) and re.match(r"^> ```\s*$", lines[i + 1]):
            i += 1

        if re.match(r"^>\s*\[![A-Z]+\]\s*$", line):
            in_alert = True
            alert_has_body = False
            out.append(line)
            i += 1
            while i < len(lines):
                current = lines[i]
                if current.strip() == "":
                    out.append(current)
                    in_alert = False
                    alert_has_body = False
                    i += 1
                    break
                if re.match(r"^>\s*\[![A-Z]+\]\s*$", current):
                    out.append("\n")
                    in_alert = True
                    alert_has_body = False
                    break
                if not current.startswith(">"):
                    current = f"> {current}"
                if current.strip() not in {">", ""} and not is_alert_marker(current):
                    alert_has_body = True
                out.append(current)
                i += 1
            continue
        elif in_alert and is_quoted_line(line):
            if line.strip() not in {">", ""} and not is_alert_marker(line):
                alert_has_body = True
        elif in_alert and line.strip() == "":
            in_alert = False
            alert_has_body = False
        elif in_alert:
            in_alert = False
            alert_has_body = False

        out.append(line)
        i += 1

    return "".join(out)


def normalize_body_h1s(front_matter: str, body: str) -> str:
    title_match = re.search(r'^title:\s*"(.*?)"\s*$', front_matter, flags=re.MULTILINE)
    if not title_match:
        return body
    title = clean_title(title_match.group(1))
    lines = body.splitlines(keepends=True)
    in_fence = False
    removed_first = False
    for idx, line in enumerate(lines):
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(\s*)#(?!#)\s*(\S.*)$", line)
        if not match:
            continue
        heading = clean_title(match.group(2))
        if not removed_first and heading == title:
            lines[idx] = ""
            removed_first = True
            continue
        lines[idx] = f"{match.group(1)}## {match.group(2)}\n"
        removed_first = True
    return "".join(lines).lstrip("\n")


def normalize_presentational_html(front_matter: str, body: str) -> tuple[str, str]:
    front_matter = re.sub(
        r'^(title:\s*")(.+?)("\s*)$',
        lambda m: f'{m.group(1)}{clean_title(m.group(2))}{m.group(3)}',
        front_matter,
        flags=re.MULTILINE,
    )

    # Remove MkDocs-era anchor scaffolding and the matching back-to-top links.
    body = re.sub(r'^\s*<a name="top"></a>\s*\n', "", body, flags=re.MULTILINE)
    body = re.sub(
        r'^\s*<p align="right"><a href="#top">.*?</a></p>\s*\n?',
        "",
        body,
        flags=re.MULTILINE,
    )

    # Strip underline-only presentation tags from prose and headings.
    body = re.sub(r"</?u>", "", body)

    # Replace a styled paragraph used as a faux H1 with semantic Markdown or
    # remove it entirely when the page title already provides the heading.
    title_match = re.search(r'^title:\s*"(.*?)"\s*$', front_matter, flags=re.MULTILINE)
    title = clean_title(title_match.group(1)) if title_match else None
    faux_h1 = re.match(r'^\s*<p style="[^"]*font-size:\s*28px;[^"]*font-weight:\s*bold;[^"]*">(.*?)</p>\s*\n?', body)
    if faux_h1:
        faux_text = clean_title(faux_h1.group(1))
        replacement = ""
        if not title or faux_text != title:
            replacement = f"# {faux_text}\n\n"
        body = replacement + body[faux_h1.end():]

    return front_matter, body


def normalize_page(path: Path) -> None:
    original = path.read_text()
    front_matter, body = split_front_matter(original)
    if not front_matter:
        return

    front_matter, body = normalize_presentational_html(front_matter, body)
    body = convert_mkdocs_blocks(body)
    body = convert_mkdocs_tabs(body)
    body = normalize_alert_syntax(body)
    body = normalize_body_h1s(front_matter, body)

    normalized = front_matter + body.lstrip("\n")
    if not normalized.endswith("\n"):
        normalized += "\n"

    path.write_text(normalized)


def main() -> None:
    for path in sorted(DOCS.rglob("*.md")):
        normalize_page(path)


if __name__ == "__main__":
    main()
