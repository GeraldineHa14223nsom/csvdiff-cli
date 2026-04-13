"""Pivot a CSV: group by a key column and aggregate a value column."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class PivotError(Exception):
    def __str__(self) -> str:  # pragma: no cover
        return f"PivotError: {self.args[0]}"


@dataclass
class PivotResult:
    row_field: str
    col_field: str
    value_field: str
    aggregation: str
    # {row_value: {col_value: aggregated_number}}
    table: Dict[str, Dict[str, float]] = field(default_factory=dict)
    col_order: List[str] = field(default_factory=list)


def _validate(rows: List[dict], row_field: str, col_field: str, value_field: str) -> None:
    if not rows:
        return
    headers = set(rows[0].keys())
    for f in (row_field, col_field, value_field):
        if f not in headers:
            raise PivotError(f"Column '{f}' not found in CSV headers: {sorted(headers)}")


def _to_float(v: str) -> float:
    try:
        return float(v)
    except (ValueError, TypeError):
        raise PivotError(f"Cannot convert value to number: {v!r}")


def pivot(
    rows: List[dict],
    row_field: str,
    col_field: str,
    value_field: str,
    aggregation: str = "sum",
) -> PivotResult:
    """Pivot *rows* producing a cross-tabulation table.

    Supported aggregations: sum, count, mean, min, max.
    """
    valid_aggs = {"sum", "count", "mean", "min", "max"}
    if aggregation not in valid_aggs:
        raise PivotError(f"Unknown aggregation '{aggregation}'. Choose from {sorted(valid_aggs)}.")

    _validate(rows, row_field, col_field, value_field)

    # Accumulate raw lists: {row_val: {col_val: [floats]}}
    buckets: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    col_seen: Dict[str, int] = {}  # preserve insertion order

    for r in rows:
        rv = r[row_field]
        cv = r[col_field]
        val = _to_float(r[value_field])
        buckets[rv][cv].append(val)
        if cv not in col_seen:
            col_seen[cv] = len(col_seen)

    col_order = sorted(col_seen, key=lambda c: col_seen[c])

    table: Dict[str, Dict[str, float]] = {}
    for rv, col_map in buckets.items():
        table[rv] = {}
        for cv, vals in col_map.items():
            if aggregation == "sum":
                table[rv][cv] = sum(vals)
            elif aggregation == "count":
                table[rv][cv] = float(len(vals))
            elif aggregation == "mean":
                table[rv][cv] = sum(vals) / len(vals)
            elif aggregation == "min":
                table[rv][cv] = min(vals)
            elif aggregation == "max":
                table[rv][cv] = max(vals)

    return PivotResult(
        row_field=row_field,
        col_field=col_field,
        value_field=value_field,
        aggregation=aggregation,
        table=table,
        col_order=col_order,
    )
