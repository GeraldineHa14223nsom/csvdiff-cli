"""Splice rows from one CSV into another at a given position."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


class SplicerError(Exception):
    def __str__(self) -> str:
        return f"SplicerError: {self.args[0]}"


@dataclass
class SpliceResult:
    rows: List[Dict[str, str]]
    headers: List[str]
    original_count: int
    inserted_count: int
    position: int

    @property
    def total_count(self) -> int:
        return len(self.rows)


def _validate(rows: List[Dict[str, str]], insert: List[Dict[str, str]], position: int) -> None:
    if position < 0:
        raise SplicerError(f"position must be >= 0, got {position}")
    if position > len(rows):
        raise SplicerError(
            f"position {position} exceeds row count {len(rows)}"
        )
    if not insert:
        raise SplicerError("insert list must not be empty")


def splice(
    rows: List[Dict[str, str]],
    insert: List[Dict[str, str]],
    position: int = 0,
    fill_value: str = "",
) -> SpliceResult:
    """Insert *insert* rows into *rows* at *position*.

    Missing keys in the inserted rows are filled with *fill_value*.
    Extra keys not present in the base headers are ignored.
    """
    _validate(rows, insert, position)

    headers: List[str] = list(rows[0].keys()) if rows else list(
        insert[0].keys() if insert else []
    )

    normalised: List[Dict[str, str]] = [
        {h: row.get(h, fill_value) for h in headers} for row in insert
    ]

    result_rows = list(rows[:position]) + normalised + list(rows[position:])

    return SpliceResult(
        rows=result_rows,
        headers=headers,
        original_count=len(rows),
        inserted_count=len(insert),
        position=position,
    )
