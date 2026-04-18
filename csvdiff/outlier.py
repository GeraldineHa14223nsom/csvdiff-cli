"""Outlier detection for numeric CSV columns using z-score or IQR methods."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any
import statistics


class OutlierError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class OutlierResult:
    rows: List[Dict[str, Any]]
    outlier_rows: List[Dict[str, Any]]
    column: str
    method: str
    threshold: float

    def outlier_count(self) -> int:
        return len(self.outlier_rows)

    def total_rows(self) -> int:
        return len(self.rows)


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        raise OutlierError(f"Non-numeric value: {value!r}")


def _validate(rows: List[Dict[str, Any]], column: str) -> None:
    if not rows:
        raise OutlierError("No rows provided")
    if column not in rows[0]:
        raise OutlierError(f"Column {column!r} not found")


def detect_outliers(
    rows: List[Dict[str, Any]],
    column: str,
    method: str = "zscore",
    threshold: float = 3.0,
) -> OutlierResult:
    _validate(rows, column)
    if method not in ("zscore", "iqr"):
        raise OutlierError(f"Unknown method {method!r}; use 'zscore' or 'iqr'")

    values = [_to_float(r[column]) for r in rows]

    if method == "zscore":
        if len(values) < 2:
            raise OutlierError("Need at least 2 rows for z-score")
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        if stdev == 0:
            outlier_rows = []
        else:
            outlier_rows = [
                r for r, v in zip(rows, values) if abs((v - mean) / stdev) > threshold
            ]
    else:  # iqr
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        q1 = sorted_vals[n // 4]
        q3 = sorted_vals[(3 * n) // 4]
        iqr = q3 - q1
        lo = q1 - threshold * iqr
        hi = q3 + threshold * iqr
        outlier_rows = [r for r, v in zip(rows, values) if v < lo or v > hi]

    return OutlierResult(
        rows=rows,
        outlier_rows=outlier_rows,
        column=column,
        method=method,
        threshold=threshold,
    )
