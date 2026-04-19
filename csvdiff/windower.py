"""Window/lag functions for CSV rows."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional


class WindowError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class WindowResult:
    rows: List[Dict[str, str]]
    column: str
    new_column: str
    lag: int
    fill: str


def windowed_row_count(result: WindowResult) -> int:
    return len(result.rows)


def _validate(rows: List[Dict[str, str]], column: str, lag: int) -> None:
    if not rows:
        return
    if column not in rows[0]:
        raise WindowError(f"Column '{column}' not found in headers.")
    if lag < 1:
        raise WindowError(f"Lag must be >= 1, got {lag}.")


def window_lag(
    rows: List[Dict[str, str]],
    column: str,
    lag: int = 1,
    new_column: Optional[str] = None,
    fill: str = "",
) -> WindowResult:
    """Add a lag column containing the value of *column* from *lag* rows ago."""
    _validate(rows, column, lag)
    out_col = new_column or f"{column}_lag{lag}"
    result_rows: List[Dict[str, str]] = []
    for i, row in enumerate(rows):
        new_row = dict(row)
        if i < lag:
            new_row[out_col] = fill
        else:
            new_row[out_col] = rows[i - lag][column]
        result_rows.append(new_row)
    return WindowResult(
        rows=result_rows,
        column=column,
        new_column=out_col,
        lag=lag,
        fill=fill,
    )
