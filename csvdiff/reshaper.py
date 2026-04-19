"""Reshape CSV rows by filling missing columns and dropping extras."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any


class ReshaperError(Exception):
    def __str__(self) -> str:
        return f"ReshaperError: {self.args[0]}"


@dataclass
class ReshapeResult:
    headers: List[str]
    rows: List[Dict[str, Any]]
    added_columns: List[str]
    dropped_columns: List[str]

    @property
    def row_count(self) -> int:
        return len(self.rows)


def _validate(target: List[str]) -> None:
    if not target:
        raise ReshaperError("target_columns must not be empty")
    if len(target) != len(set(target)):
        raise ReshaperError("target_columns contains duplicates")


def reshape(
    rows: List[Dict[str, Any]],
    target_columns: List[str],
    fill_value: str = "",
) -> ReshapeResult:
    """Reorder and reshape rows to match target_columns.

    Missing columns are filled with fill_value; extra columns are dropped.
    """
    _validate(target_columns)

    if not rows:
        return ReshapeResult(
            headers=target_columns,
            rows=[],
            added_columns=target_columns[:],
            dropped_columns=[],
        )

    existing = set(rows[0].keys())
    target_set = set(target_columns)
    added = [c for c in target_columns if c not in existing]
    dropped = [c for c in existing if c not in target_set]

    reshaped = [
        {col: row.get(col, fill_value) for col in target_columns}
        for row in rows
    ]

    return ReshapeResult(
        headers=target_columns,
        rows=reshaped,
        added_columns=added,
        dropped_columns=dropped,
    )
