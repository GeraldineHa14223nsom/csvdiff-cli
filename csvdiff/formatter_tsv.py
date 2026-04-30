"""TSV (Tab-Separated Values) formatter for diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from csvdiff.core import DiffResult


@dataclass
class TsvOptions:
    title: str = "CSV Diff Report"
    max_cell_width: int = 60
    include_section_headers: bool = True


def _truncate(value: str, max_width: int) -> str:
    if len(value) <= max_width:
        return value
    return value[: max_width - 3] + "..."


def _tsv_row(row: dict, headers: List[str], max_width: int) -> str:
    cells = [_truncate(str(row.get(h, "")), max_width) for h in headers]
    return "\t".join(cells)


def _section_lines(
    label: str,
    rows: List[dict],
    headers: List[str],
    opts: TsvOptions,
) -> List[str]:
    if not rows:
        return []
    lines: List[str] = []
    if opts.include_section_headers:
        lines.append(f"# {label}")
    lines.append("\t".join(headers))
    for row in rows:
        lines.append(_tsv_row(row, headers, opts.max_cell_width))
    return lines


def format_tsv(result: DiffResult, opts: TsvOptions | None = None) -> str:
    """Render a DiffResult as TSV text with labelled sections."""
    if opts is None:
        opts = TsvOptions()

    all_rows = (
        list(result.added)
        + list(result.removed)
        + [r["new"] for r in result.modified]
        + list(result.unchanged)
    )
    if not all_rows:
        return ""

    headers = list(all_rows[0].keys())
    sections: List[str] = []

    if opts.include_section_headers:
        sections.append(f"# {opts.title}")
        sections.append("")

    for label, rows in [
        ("ADDED", list(result.added)),
        ("REMOVED", list(result.removed)),
        ("MODIFIED", [r["new"] for r in result.modified]),
        ("UNCHANGED", list(result.unchanged)),
    ]:
        block = _section_lines(label, rows, headers, opts)
        if block:
            sections.extend(block)
            sections.append("")

    return "\n".join(sections).rstrip() + "\n"
