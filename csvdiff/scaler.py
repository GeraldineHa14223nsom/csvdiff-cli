"""Scale numeric columns using min-max or z-score normalization."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Sequence


class ScalerError(Exception):
    def __str__(self) -> str:
        return f"ScalerError: {self.args[0]}"


@dataclass
class ScaleResult:
    rows: List[Dict[str, str]]
    column: str
    method: str
    scaled_count: int
    original_min: float
    original_max: float

    @property
    def row_count(self) -> int:
        return len(self.rows)


def _validate(rows: Sequence[Dict[str, str]], column: str) -> None:
    if not rows:
        raise ScalerError("rows must not be empty")
    if column not in rows[0]:
        raise ScalerError(f"column '{column}' not found in headers")


def _to_float(value: str, column: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ScalerError(f"non-numeric value '{value}' in column '{column}'")


def scale(rows: Sequence[Dict[str, str]], column: str, method: str = "minmax") -> ScaleResult:
    """Scale *column* in-place using *method* ('minmax' or 'zscore')."""
    if method not in ("minmax", "zscore"):
        raise ScalerError(f"unknown method '{method}'; choose 'minmax' or 'zscore'")
    _validate(rows, column)

    values = [_to_float(r[column], column) for r in rows]
    orig_min = min(values)
    orig_max = max(values)

    if method == "minmax":
        span = orig_max - orig_min
        if span == 0.0:
            scaled = [0.0] * len(values)
        else:
            scaled = [(v - orig_min) / span for v in values]
    else:  # zscore
        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        std = variance ** 0.5
        if std == 0.0:
            scaled = [0.0] * len(values)
        else:
            scaled = [(v - mean) / std for v in values]

    out_rows = [
        {**r, column: f"{s:.6g}"}
        for r, s in zip(rows, scaled)
    ]
    return ScaleResult(
        rows=out_rows,
        column=column,
        method=method,
        scaled_count=len(out_rows),
        original_min=orig_min,
        original_max=orig_max,
    )
