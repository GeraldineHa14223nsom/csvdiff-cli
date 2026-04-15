"""Flatten nested JSON-like string values in CSV columns into separate columns."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


class FlattenerError(Exception):
    def __str__(self) -> str:
        return f"FlattenerError: {self.args[0]}"


@dataclass
class FlattenResult:
    headers: list[str]
    rows: list[dict[str, str]]
    new_columns: list[str]
    source_column: str


def _parse_json_cell(value: str) -> dict[str, Any] | None:
    """Try to parse a cell value as JSON object; return None on failure."""
    try:
        parsed = json.loads(value)
        if isinstance(parsed, dict):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    return None


def _validate(rows: list[dict[str, str]], column: str) -> None:
    if not rows:
        raise FlattenerError("rows must not be empty")
    if column not in rows[0]:
        raise FlattenerError(f"column '{column}' not found in headers")


def flatten_column(
    rows: list[dict[str, str]],
    column: str,
    prefix: str = "",
    drop_source: bool = False,
) -> FlattenResult:
    """Flatten JSON object values from *column* into individual columns."""
    _validate(rows, column)

    new_col_names: list[str] = []
    expanded: list[dict[str, str]] = []

    for row in rows:
        parsed = _parse_json_cell(row.get(column, ""))
        if parsed:
            for k in parsed:
                col_name = f"{prefix}{k}" if prefix else k
                if col_name not in new_col_names:
                    new_col_names.append(col_name)

    for row in rows:
        new_row = dict(row)
        parsed = _parse_json_cell(row.get(column, ""))
        if parsed:
            for k, v in parsed.items():
                col_name = f"{prefix}{k}" if prefix else k
                new_row[col_name] = str(v)
        else:
            for col_name in new_col_names:
                new_row.setdefault(col_name, "")
        if drop_source:
            new_row.pop(column, None)
        expanded.append(new_row)

    base_headers = [h for h in rows[0].keys() if not (drop_source and h == column)]
    headers = base_headers + [c for c in new_col_names if c not in base_headers]

    return FlattenResult(
        headers=headers,
        rows=expanded,
        new_columns=new_col_names,
        source_column=column,
    )
