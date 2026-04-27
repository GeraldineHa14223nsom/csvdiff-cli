"""Pad CSV rows so every row has the same set of columns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any


class PadderError(Exception):
    def __str__(self) -> str:
        return f"PadderError: {self.args[0]}"


@dataclass
class PadResult:
    headers: List[str]
    rows: List[Dict[str, Any]]
    added_columns: List[str]
    fill_value: str

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def added_column_count(self) -> int:
        return len(self.added_columns)


def _validate(headers: List[str], extra: List[str]) -> None:
    if not headers and not extra:
        raise PadderError("at least one column must be present")
    overlap = set(headers) & set(extra)
    if overlap:
        raise PadderError(
            f"extra columns already exist in headers: {sorted(overlap)}"
        )


def pad_columns(
    headers: List[str],
    rows: List[Dict[str, Any]],
    extra_columns: List[str],
    fill_value: str = "",
) -> PadResult:
    """Add *extra_columns* to every row, filling missing values with *fill_value*."""
    _validate(headers, extra_columns)
    new_headers = headers + extra_columns
    padded: List[Dict[str, Any]] = []
    for row in rows:
        new_row = dict(row)
        for col in extra_columns:
            new_row.setdefault(col, fill_value)
        padded.append(new_row)
    return PadResult(
        headers=new_headers,
        rows=padded,
        added_columns=list(extra_columns),
        fill_value=fill_value,
    )


def pad_to_union(
    headers_a: List[str],
    rows_a: List[Dict[str, Any]],
    headers_b: List[str],
    rows_b: List[Dict[str, Any]],
    fill_value: str = "",
) -> tuple[PadResult, PadResult]:
    """Pad both row sets so they share the same full union of columns."""
    all_cols: List[str] = list(dict.fromkeys(headers_a + headers_b))
    extra_a = [c for c in all_cols if c not in headers_a]
    extra_b = [c for c in all_cols if c not in headers_b]
    result_a = pad_columns(headers_a, rows_a, extra_a, fill_value)
    result_b = pad_columns(headers_b, rows_b, extra_b, fill_value)
    return result_a, result_b
