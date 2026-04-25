"""Assign sequential row numbers or custom sequences to CSV rows."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional


class SequencerError(Exception):
    def __str__(self) -> str:
        return f"SequencerError: {self.args[0]}"


@dataclass
class SequenceResult:
    rows: List[Dict[str, str]]
    column: str
    start: int
    step: int
    original_count: int

    @property
    def row_count(self) -> int:
        return len(self.rows)


def _validate(column: str, rows: List[Dict[str, str]], step: int) -> None:
    if not column:
        raise SequencerError("column name must not be empty")
    if step == 0:
        raise SequencerError("step must not be zero")
    if rows and column in rows[0]:
        raise SequencerError(f"column '{column}' already exists in data")


def sequence_rows(
    rows: List[Dict[str, str]],
    column: str = "seq",
    start: int = 1,
    step: int = 1,
    overwrite: bool = False,
) -> SequenceResult:
    """Prepend a sequential integer column to each row.

    Args:
        rows: Input rows as list of dicts.
        column: Name of the new sequence column.
        start: Starting value of the sequence.
        step: Increment between successive values.
        overwrite: If True, allow overwriting an existing column.

    Returns:
        SequenceResult containing annotated rows.
    """
    if not overwrite:
        _validate(column, rows, step)
    elif step == 0:
        raise SequencerError("step must not be zero")
    elif not column:
        raise SequencerError("column name must not be empty")

    sequenced: List[Dict[str, str]] = []
    value = start
    for row in rows:
        new_row = {column: str(value)}
        new_row.update(row)
        sequenced.append(new_row)
        value += step

    return SequenceResult(
        rows=sequenced,
        column=column,
        start=start,
        step=step,
        original_count=len(rows),
    )
