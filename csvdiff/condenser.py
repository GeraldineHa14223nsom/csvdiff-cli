"""Condense CSV rows by aggregating repeated key values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence


class CondenserError(Exception):
    def __str__(self) -> str:
        return f"CondenserError: {self.args[0]}"


@dataclass
class CondenseResult:
    headers: List[str]
    rows: List[Dict[str, str]]
    original_count: int
    condensed_count: int
    key_columns: List[str]
    agg_column: str
    separator: str

    @property
    def reduction_count(self) -> int:
        return self.original_count - self.condensed_count

    @property
    def reduction_rate(self) -> float:
        if self.original_count == 0:
            return 0.0
        return self.reduction_count / self.original_count


def _validate(
    headers: List[str],
    key_columns: List[str],
    agg_column: str,
) -> None:
    for col in key_columns:
        if col not in headers:
            raise CondenserError(f"Key column '{col}' not found in headers")
    if agg_column not in headers:
        raise CondenserError(f"Aggregate column '{agg_column}' not found in headers")
    if agg_column in key_columns:
        raise CondenserError(
            f"Aggregate column '{agg_column}' cannot also be a key column"
        )


def condense(
    rows: Sequence[Dict[str, str]],
    key_columns: List[str],
    agg_column: str,
    separator: str = "|",
) -> CondenseResult:
    """Group rows by key_columns and join agg_column values with separator."""
    if not rows:
        headers: List[str] = []
        return CondenseResult(
            headers=headers,
            rows=[],
            original_count=0,
            condensed_count=0,
            key_columns=key_columns,
            agg_column=agg_column,
            separator=separator,
        )

    headers = list(rows[0].keys())
    _validate(headers, key_columns, agg_column)

    grouped: Dict[tuple, List[str]] = {}
    first_row: Dict[tuple, Dict[str, str]] = {}

    for row in rows:
        key = tuple(row[k] for k in key_columns)
        if key not in grouped:
            grouped[key] = []
            first_row[key] = row
        grouped[key].append(row[agg_column])

    condensed: List[Dict[str, str]] = []
    for key, values in grouped.items():
        new_row = dict(first_row[key])
        new_row[agg_column] = separator.join(values)
        condensed.append(new_row)

    return CondenseResult(
        headers=headers,
        rows=condensed,
        original_count=len(rows),
        condensed_count=len(condensed),
        key_columns=key_columns,
        agg_column=agg_column,
        separator=separator,
    )
