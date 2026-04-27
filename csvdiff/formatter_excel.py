"""Excel-compatible CSV formatter for diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from csvdiff.core import DiffResult


@dataclass
class ExcelOptions:
    max_col_width: int = 64
    sheet_label_added: str = "Added"
    sheet_label_removed: str = "Removed"
    sheet_label_modified: str = "Modified"
    sheet_label_unchanged: str = "Unchanged"
    include_unchanged: bool = False
    extra_headers: Dict[str, str] = field(default_factory=dict)


def _truncate(value: str, width: int) -> str:
    if len(value) <= width:
        return value
    return value[: width - 1] + "…"


def _row_to_cells(row: dict, headers: List[str], width: int) -> List[str]:
    return [_truncate(str(row.get(h, "")), width) for h in headers]


def _section_lines(label: str, rows: List[dict], opts: ExcelOptions) -> List[str]:
    if not rows:
        return []
    headers = list(rows[0].keys())
    lines: List[str] = []
    lines.append(f"## {label}")
    lines.append(",".join(headers))
    for row in rows:
        cells = _row_to_cells(row, headers, opts.max_col_width)
        lines.append(",".join(cells))
    lines.append("")
    return lines


def format_excel_csv(result: DiffResult, opts: ExcelOptions | None = None) -> str:
    """Return a multi-section CSV string suitable for pasting into Excel.

    Each diff category is separated by a labelled header row so that
    a user can split the output into named regions inside a spreadsheet.
    """
    if opts is None:
        opts = ExcelOptions()

    sections: List[str] = []
    sections += _section_lines(opts.sheet_label_added, result.added, opts)
    sections += _section_lines(opts.sheet_label_removed, result.removed, opts)

    modified_flat = [
        {"key": k, **old, **{f"{col}_new": new[col] for col in new}}
        for k, (old, new) in result.modified.items()
    ]
    sections += _section_lines(opts.sheet_label_modified, modified_flat, opts)

    if opts.include_unchanged:
        sections += _section_lines(opts.sheet_label_unchanged, result.unchanged, opts)

    return "\n".join(sections).rstrip() + "\n"
