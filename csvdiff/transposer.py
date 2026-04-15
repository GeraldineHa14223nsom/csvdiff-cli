"""Transpose CSV rows into columns and vice versa."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


class TransposerError(Exception):
    def __str__(self) -> str:
        return f"TransposerError: {self.args[0]}"


@dataclass
class TransposeResult:
    headers: List[str]
    rows: List[Dict[str, str]]
    original_row_count: int
    original_col_count: int


def _validate(headers: List[str], rows: List[Dict[str, str]]) -> None:
    if not headers:
        raise TransposerError("Cannot transpose: no columns found.")
    if not rows:
        raise TransposerError("Cannot transpose: no rows found.")


def transpose(headers: List[str], rows: List[Dict[str, str]]) -> TransposeResult:
    """Transpose a CSV so that each original column becomes a row.

    The output has columns: 'field' plus one column per original row,
    named 'row_0', 'row_1', ...
    """
    _validate(headers, rows)

    original_row_count = len(rows)
    original_col_count = len(headers)

    new_headers = ["field"] + [f"row_{i}" for i in range(original_row_count)]

    new_rows: List[Dict[str, str]] = []
    for col in headers:
        new_row: Dict[str, str] = {"field": col}
        for i, row in enumerate(rows):
            new_row[f"row_{i}"] = row.get(col, "")
        new_rows.append(new_row)

    return TransposeResult(
        headers=new_headers,
        rows=new_rows,
        original_row_count=original_row_count,
        original_col_count=original_col_count,
    )
