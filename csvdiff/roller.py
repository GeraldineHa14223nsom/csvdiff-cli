"""Rolling window calculations for CSV columns."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any


class RollerError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class RollResult:
    rows: List[Dict[str, Any]]
    column: str
    window: int
    new_column: str
    computed: int


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        raise RollerError(f"Non-numeric value: {value!r}")


def _validate(rows: list, column: str, window: int) -> None:
    if window < 1:
        raise RollerError(f"Window must be >= 1, got {window}")
    if not rows:
        return
    if column not in rows[0]:
        raise RollerError(f"Column {column!r} not found")


def rolling(rows: List[Dict[str, Any]], column: str, window: int,
            func: str = "mean", new_column: str | None = None) -> RollResult:
    """Compute a rolling statistic over a numeric column."""
    _validate(rows, column, window)
    funcs = {
        "mean": lambda vs: sum(vs) / len(vs),
        "sum": sum,
        "min": min,
        "max": max,
    }
    if func not in funcs:
        raise RollerError(f"Unknown function {func!r}. Choose from: {list(funcs)}")
    agg = funcs[func]
    col_name = new_column or f"{column}_rolling_{func}_{window}"
    out = []
    computed = 0
    for i, row in enumerate(rows):
        new_row = dict(row)
        if i + 1 < window:
            new_row[col_name] = ""
        else:
            window_vals = [_to_float(rows[j][column]) for j in range(i - window + 1, i + 1)]
            new_row[col_name] = str(round(agg(window_vals), 6))
            computed += 1
        out.append(new_row)
    return RollResult(rows=out, column=column, window=window, new_column=col_name, computed=computed)
