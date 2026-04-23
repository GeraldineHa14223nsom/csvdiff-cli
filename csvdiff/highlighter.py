"""Highlight cells in a CSV that match a pattern or condition."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class HighlighterError(Exception):
    def __str__(self) -> str:
        return f"HighlighterError: {self.args[0]}"


@dataclass
class HighlightResult:
    rows: List[Dict[str, str]]
    flagged: List[Dict[str, str]]
    column: str
    pattern: str
    match_count: int = field(init=False)

    def __post_init__(self) -> None:
        self.match_count = len(self.flagged)


def match_rate(result: HighlightResult) -> float:
    if not result.rows:
        return 0.0
    return result.match_count / len(result.rows)


def _validate(rows: List[Dict[str, str]], column: str) -> None:
    if not rows:
        return
    if column not in rows[0]:
        raise HighlighterError(f"Column '{column}' not found in headers")


def highlight(
    rows: List[Dict[str, str]],
    column: str,
    pattern: str,
    highlight_column: str = "_highlight",
    case_sensitive: bool = False,
) -> HighlightResult:
    """Tag rows whose *column* value matches *pattern* (regex).

    A new column *highlight_column* is added to every row; its value is
    ``"1"`` when the cell matches and ``"0"`` otherwise.
    """
    _validate(rows, column)

    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        compiled = re.compile(pattern, flags)
    except re.error as exc:
        raise HighlighterError(f"Invalid regex pattern: {exc}") from exc

    out_rows: List[Dict[str, str]] = []
    flagged: List[Dict[str, str]] = []

    for row in rows:
        value = row.get(column, "")
        matched = bool(compiled.search(value))
        new_row = {**row, highlight_column: "1" if matched else "0"}
        out_rows.append(new_row)
        if matched:
            flagged.append(new_row)

    return HighlightResult(
        rows=out_rows,
        flagged=flagged,
        column=column,
        pattern=pattern,
    )
