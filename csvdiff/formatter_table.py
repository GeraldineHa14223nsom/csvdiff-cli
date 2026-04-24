"""Pretty-print CSV diff results as an ASCII table."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from csvdiff.core import DiffResult


@dataclass
class TableOptions:
    max_col_width: int = 24
    show_unchanged: bool = False
    separator: str = "|"


def _truncate(value: str, width: int) -> str:
    if len(value) <= width:
        return value
    return value[: width - 1] + "…"


def _row_to_cells(row: dict, headers: List[str], width: int) -> List[str]:
    return [_truncate(str(row.get(h, "")), width) for h in headers]


def _build_table(rows: Sequence[dict], tag: str, headers: List[str], opts: TableOptions) -> List[str]:
    if not rows:
        return []
    w = opts.max_col_width
    sep = opts.separator
    col_widths = [max(len(h), 4) for h in headers]
    for row in rows:
        for i, h in enumerate(headers):
            col_widths[i] = min(w, max(col_widths[i], len(str(row.get(h, "")))))
    header_line = " " + f" {sep} ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    divider = "-" + "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    lines = [f"[{tag}]", header_line, divider]
    for row in rows:
        cells = [_truncate(str(row.get(h, "")), col_widths[i]).ljust(col_widths[i]) for i, h in enumerate(headers)]
        lines.append(" " + f" {sep} ".join(cells))
    return lines


def format_table(result: DiffResult, opts: TableOptions | None = None) -> str:
    """Return a multi-section ASCII table string for a DiffResult."""
    if opts is None:
        opts = TableOptions()

    sections: List[str] = []

    all_rows = (
        list(result.added)
        + list(result.removed)
        + [r["new"] for r in result.modified]
    )
    if opts.show_unchanged:
        all_rows += list(result.unchanged)

    if not all_rows:
        return "(no differences)"

    headers: List[str] = []
    for row in all_rows:
        for k in row:
            if k not in headers:
                headers.append(k)

    if result.added:
        sections.extend(_build_table(list(result.added), "ADDED", headers, opts))
        sections.append("")

    if result.removed:
        sections.extend(_build_table(list(result.removed), "REMOVED", headers, opts))
        sections.append("")

    if result.modified:
        new_rows = [r["new"] for r in result.modified]
        sections.extend(_build_table(new_rows, "MODIFIED", headers, opts))
        sections.append("")

    if opts.show_unchanged and result.unchanged:
        sections.extend(_build_table(list(result.unchanged), "UNCHANGED", headers, opts))
        sections.append("")

    return "\n".join(sections).rstrip()
