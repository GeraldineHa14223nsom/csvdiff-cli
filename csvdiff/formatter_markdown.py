"""Markdown table formatter for DiffResult."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from csvdiff.core import DiffResult


@dataclass
class MarkdownOptions:
    max_col_width: int = 40
    show_section_headers: bool = True
    sections: List[str] = field(
        default_factory=lambda: ["added", "removed", "modified"]
    )


def _truncate(value: str, width: int) -> str:
    if len(value) <= width:
        return value
    return value[: width - 1] + "…"


def _md_row(cells: List[str], widths: List[int]) -> str:
    padded = [_truncate(c, widths[i]).ljust(widths[i]) for i, c in enumerate(cells)]
    return "| " + " | ".join(padded) + " |"


def _md_separator(widths: List[int]) -> str:
    return "| " + " | ".join("-" * w for w in widths) + " |"


def _build_section(
    title: str,
    rows: List[dict],
    headers: List[str],
    options: MarkdownOptions,
) -> str:
    if not rows:
        return ""

    lines: List[str] = []
    if options.show_section_headers:
        lines.append(f"### {title}")
        lines.append("")

    widths = [max(len(h), 4) for h in headers]
    for row in rows:
        for i, h in enumerate(headers):
            val = str(row.get(h, ""))
            widths[i] = min(max(widths[i], len(val)), options.max_col_width)

    lines.append(_md_row(headers, widths))
    lines.append(_md_separator(widths))
    for row in rows:
        cells = [str(row.get(h, "")) for h in headers]
        lines.append(_md_row(cells, widths))
    lines.append("")
    return "\n".join(lines)


def format_markdown(result: DiffResult, options: MarkdownOptions | None = None) -> str:
    """Return a Markdown-formatted diff report."""
    if options is None:
        options = MarkdownOptions()

    parts: List[str] = []

    all_rows = result.added + result.removed + result.modified + result.unchanged
    headers: List[str] = []
    if all_rows:
        headers = list(all_rows[0].keys())

    section_map = {
        "added": ("Added", result.added),
        "removed": ("Removed", result.removed),
        "modified": ("Modified", result.modified),
        "unchanged": ("Unchanged", result.unchanged),
    }

    for key in options.sections:
        if key in section_map:
            title, rows = section_map[key]
            section = _build_section(title, rows, headers, options)
            if section:
                parts.append(section)

    return "\n".join(parts)
