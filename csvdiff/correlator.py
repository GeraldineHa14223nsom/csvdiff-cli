"""Compute pairwise Pearson correlation between numeric columns."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Sequence


class CorrelatorError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class CorrelationResult:
    columns: List[str]
    matrix: Dict[str, Dict[str, float]]


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        raise CorrelatorError(f"Non-numeric value: {value!r}")


def _pearson(xs: List[float], ys: List[float]) -> float:
    n = len(xs)
    if n < 2:
        return float("nan")
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return float("nan")
    return num / (dx * dy)


def correlate(
    rows: Sequence[Dict[str, str]],
    columns: List[str],
) -> CorrelationResult:
    if not rows:
        raise CorrelatorError("No rows to correlate.")
    headers = list(rows[0].keys())
    for col in columns:
        if col not in headers:
            raise CorrelatorError(f"Column not found: {col!r}")
    if len(columns) < 2:
        raise CorrelatorError("At least two columns are required.")

    vectors: Dict[str, List[float]] = {
        col: [_to_float(r[col]) for r in rows] for col in columns
    }

    matrix: Dict[str, Dict[str, float]] = {}
    for a in columns:
        matrix[a] = {}
        for b in columns:
            matrix[a][b] = round(_pearson(vectors[a], vectors[b]), 6)

    return CorrelationResult(columns=columns, matrix=matrix)
