"""HTML table formatter for diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from csvdiff.core import DiffResult


@dataclass
class HtmlOptions:
    title: str = "CSV Diff Report"
    max_rows: int = 200
    show_unchanged: bool = False
    css_class: str = "csvdiff"


_LABEL: Dict[str, str] = {
    "added": "added",
    "removed": "removed",
    "modified": "modified",
    "unchanged": "unchanged",
}


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _row_html(row: dict, kind: str, css_class: str) -> str:
    cells = "".join(f"<td>{_escape(str(v))}</td>" for v in row.values())
    return f'<tr class="{css_class}-{_LABEL[kind]}">{cells}</tr>\n'


def _header_html(headers: List[str], css_class: str) -> str:
    cells = "".join(f"<th>{_escape(h)}</th>" for h in headers)
    return f'<tr class="{css_class}-header">{cells}</tr>\n'


def format_html(result: DiffResult, options: HtmlOptions | None = None) -> str:
    if options is None:
        options = HtmlOptions()

    all_rows: List[tuple] = []
    for row in result.added[:options.max_rows]:
        all_rows.append((row, "added"))
    for row in result.removed[:options.max_rows]:
        all_rows.append((row, "removed"))
    for row in result.modified[:options.max_rows]:
        all_rows.append((row, "modified"))
    if options.show_unchanged:
        for row in result.unchanged[:options.max_rows]:
            all_rows.append((row, "unchanged"))

    if not all_rows:
        body = f'<tr><td colspan="1" class="{options.css_class}-empty">No differences found.</td></tr>\n'
        headers_html = ""
    else:
        headers = list(all_rows[0][0].keys())
        headers_html = _header_html(headers, options.css_class)
        body = "".join(_row_html(row, kind, options.css_class) for row, kind in all_rows)

    return (
        f"<!DOCTYPE html>\n<html>\n<head><title>{_escape(options.title)}</title></head>\n"
        f"<body>\n"
        f'<table class="{options.css_class}">\n'
        f"<thead>{headers_html}</thead>\n"
        f"<tbody>\n{body}</tbody>\n"
        f"</table>\n</body>\n</html>\n"
    )
