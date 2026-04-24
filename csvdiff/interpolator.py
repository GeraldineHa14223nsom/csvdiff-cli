"""Fill gaps in numeric columns using linear interpolation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional


class InterpolatorError(Exception):
    def __str__(self) -> str:
        return f"InterpolatorError: {self.args[0]}"


@dataclass
class InterpolateResult:
    headers: List[str]
    rows: List[Dict[str, str]]
    filled_count: int
    columns: List[str]


def _validate(rows: List[Dict[str, str]], columns: List[str]) -> None:
    if not columns:
        raise InterpolatorError("at least one column must be specified")
    if not rows:
        return
    available = set(rows[0].keys())
    for col in columns:
        if col not in available:
            raise InterpolatorError(f"column '{col}' not found in data")


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def interpolate(rows: List[Dict[str, str]], columns: List[str]) -> InterpolateResult:
    """Linearly interpolate missing (empty) values in *columns*.

    A cell is considered missing when it is an empty string.  Values at the
    edges that have no valid neighbour on one side are left empty.
    """
    if not rows:
        headers: List[str] = []
        return InterpolateResult(headers=headers, rows=[], filled_count=0, columns=columns)

    _validate(rows, columns)
    headers = list(rows[0].keys())
    result = [dict(r) for r in rows]
    filled_count = 0

    for col in columns:
        values: List[Optional[float]] = [_to_float(r[col]) for r in result]
        n = len(values)

        for i in range(n):
            if values[i] is not None:
                continue
            # find previous known index
            prev_i, prev_v = None, None
            for j in range(i - 1, -1, -1):
                if values[j] is not None:
                    prev_i, prev_v = j, values[j]
                    break
            # find next known index
            next_i, next_v = None, None
            for j in range(i + 1, n):
                if values[j] is not None:
                    next_i, next_v = j, values[j]
                    break

            if prev_i is None or next_i is None:
                continue  # edge gap — leave empty

            span = next_i - prev_i
            interpolated = prev_v + (next_v - prev_v) * (i - prev_i) / span  # type: ignore[operator]
            values[i] = interpolated
            result[i][col] = str(interpolated)
            filled_count += 1

    return InterpolateResult(
        headers=headers,
        rows=result,
        filled_count=filled_count,
        columns=columns,
    )
