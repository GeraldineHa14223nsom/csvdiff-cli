"""Unpivot (melt) a CSV: turn column headers into row values."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Sequence


class UnpivotError(Exception):
    def __str__(self) -> str:
        return f"UnpivotError: {self.args[0]}"


@dataclass
class UnpivotResult:
    headers: List[str]
    rows: List[Dict[str, str]]
    original_row_count: int
    value_columns: List[str]


def unpivoted_row_count(result: UnpivotResult) -> int:
    return len(result.rows)


def _validate(headers: List[str], id_columns: List[str], value_columns: List[str]) -> None:
    for col in id_columns:
        if col not in headers:
            raise UnpivotError(f"id column '{col}' not found in headers")
    for col in value_columns:
        if col not in headers:
            raise UnpivotError(f"value column '{col}' not found in headers")
    if not value_columns:
        raise UnpivotError("at least one value column must be specified")


def unpivot(
    rows: List[Dict[str, str]],
    id_columns: Sequence[str],
    value_columns: Sequence[str],
    var_name: str = "variable",
    value_name: str = "value",
) -> UnpivotResult:
    """Melt wide-format rows into long format."""
    if not rows:
        headers = list(id_columns) + [var_name, value_name]
        return UnpivotResult(headers=headers, rows=[], original_row_count=0,
                             value_columns=list(value_columns))

    all_headers = list(rows[0].keys())
    id_cols = list(id_columns)
    val_cols = list(value_columns)
    _validate(all_headers, id_cols, val_cols)

    out_headers = id_cols + [var_name, value_name]
    out_rows: List[Dict[str, str]] = []

    for row in rows:
        id_part = {c: row[c] for c in id_cols}
        for vc in val_cols:
            new_row = dict(id_part)
            new_row[var_name] = vc
            new_row[value_name] = row.get(vc, "")
            out_rows.append(new_row)

    return UnpivotResult(
        headers=out_headers,
        rows=out_rows,
        original_row_count=len(rows),
        value_columns=val_cols,
    )
