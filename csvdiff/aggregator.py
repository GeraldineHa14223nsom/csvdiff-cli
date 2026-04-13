"""Column aggregation utilities for CSV diff results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class AggregatorError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class AggregateResult:
    column: str
    count: int
    total: float
    minimum: Optional[float]
    maximum: Optional[float]
    mean: Optional[float]


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def aggregate_column(
    rows: List[Dict[str, str]],
    column: str,
) -> AggregateResult:
    """Compute count, sum, min, max, and mean for *column* across *rows*."""
    if not rows:
        raise AggregatorError(f"No rows provided for column '{column}'.")
    if column not in rows[0]:
        raise AggregatorError(f"Column '{column}' not found in rows.")

    numeric_values: List[float] = []
    for row in rows:
        val = _to_float(row.get(column, ""))
        if val is not None:
            numeric_values.append(val)

    count = len(numeric_values)
    if count == 0:
        return AggregateResult(
            column=column,
            count=0,
            total=0.0,
            minimum=None,
            maximum=None,
            mean=None,
        )

    total = sum(numeric_values)
    return AggregateResult(
        column=column,
        count=count,
        total=total,
        minimum=min(numeric_values),
        maximum=max(numeric_values),
        mean=total / count,
    )


def aggregate_all(
    rows: List[Dict[str, str]],
    columns: List[str],
) -> Dict[str, AggregateResult]:
    """Run :func:`aggregate_column` for each column in *columns*."""
    return {col: aggregate_column(rows, col) for col in columns}
