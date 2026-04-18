"""Fill missing (empty) values in CSV columns."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional


class ImputerError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class ImputeResult:
    headers: List[str]
    rows: List[Dict[str, str]]
    filled_count: int
    column_counts: Dict[str, int]


def _validate(headers: List[str], fill_map: Dict[str, str]) -> None:
    unknown = set(fill_map) - set(headers)
    if unknown:
        raise ImputerError(f"Unknown columns: {', '.join(sorted(unknown))}")


def impute(
    headers: List[str],
    rows: List[Dict[str, str]],
    fill_map: Optional[Dict[str, str]] = None,
    fill_value: str = "",
    columns: Optional[List[str]] = None,
) -> ImputeResult:
    """Fill empty cells.

    fill_map: per-column fill values (takes precedence).
    fill_value: default fill value for columns listed in *columns* (or all).
    columns: restrict filling to these columns when using fill_value.
    """
    effective_map: Dict[str, str] = {}
    target_cols = columns if columns is not None else headers
    for col in target_cols:
        effective_map[col] = fill_value
    if fill_map:
        _validate(headers, fill_map)
        effective_map.update(fill_map)

    filled_count = 0
    column_counts: Dict[str, int] = {col: 0 for col in effective_map}
    out_rows: List[Dict[str, str]] = []

    for row in rows:
        new_row = dict(row)
        for col, val in effective_map.items():
            if col in new_row and new_row[col] == "":
                new_row[col] = val
                column_counts[col] += 1
                filled_count += 1
        out_rows.append(new_row)

    return ImputeResult(
        headers=headers,
        rows=out_rows,
        filled_count=filled_count,
        column_counts=column_counts,
    )
