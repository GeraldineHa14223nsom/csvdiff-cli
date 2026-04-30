"""LaTeX tabular formatter for diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from csvdiff.core import DiffResult


@dataclass
class LatexOptions:
    title: str = "CSV Diff Report"
    max_col_width: int = 40
    show_unchanged: bool = False
    caption: str = ""
    label: str = "tab:csvdiff"


def _truncate(value: str, width: int) -> str:
    if len(value) <= width:
        return value
    return value[: width - 3] + "..."


def _escape(value: str) -> str:
    """Escape special LaTeX characters."""
    replacements = [
        ("\\", "\\textbackslash{}"),
        ("&", "\\&"),
        ("%", "\\%"),
        ("$", "\\$"),
        ("#", "\\#"),
        ("_", "\\_"),
        ("{", "\\{"),
        ("}", "\\}"),
        ("~", "\\textasciitilde{}"),
        ("^", "\\textasciicircum{}"),
    ]
    for char, replacement in replacements:
        value = value.replace(char, replacement)
    return value


def _row_latex(row: dict, headers: List[str], width: int) -> str:
    cells = [_escape(_truncate(str(row.get(h, "")), width)) for h in headers]
    return " & ".join(cells) + " \\\\"


def _section_latex(
    rows: List[dict], headers: List[str], section_title: str, opts: LatexOptions
) -> List[str]:
    if not rows:
        return []
    lines = []
    col_spec = "|".join(["l"] * len(headers))
    lines.append(f"\\subsection*{{{_escape(section_title)}}}")
    lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
    lines.append("\\hline")
    header_row = " & ".join(_escape(h) for h in headers) + " \\\\"
    lines.append(header_row)
    lines.append("\\hline")
    for row in rows:
        lines.append(_row_latex(row, headers, opts.max_col_width))
    lines.append("\\hline")
    lines.append("\\end{tabular}")
    lines.append("")
    return lines


def format_latex(result: DiffResult, opts: LatexOptions | None = None) -> str:
    if opts is None:
        opts = LatexOptions()

    all_rows = (
        result.added + result.removed
        + [m["new"] for m in result.modified]
        + result.unchanged
    )
    headers: List[str] = []
    if all_rows:
        headers = list(all_rows[0].keys())

    lines: List[str] = []
    lines.append("\\section*{" + _escape(opts.title) + "}")
    lines.append("")

    lines.extend(_section_latex(result.added, headers, "Added Rows", opts))
    lines.extend(_section_latex(result.removed, headers, "Removed Rows", opts))

    modified_rows = [m["new"] for m in result.modified]
    lines.extend(_section_latex(modified_rows, headers, "Modified Rows (new values)", opts))

    if opts.show_unchanged:
        lines.extend(_section_latex(result.unchanged, headers, "Unchanged Rows", opts))

    return "\n".join(lines)
