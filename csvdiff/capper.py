"""Cap (limit) the number of rows per group defined by a key column."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


class CapperError(Exception):
    def __str__(self) -> str:  # pragma: no cover
        return f"CapperError: {self.args[0]}"


@dataclass
class CapResult:
    rows: List[Dict[str, str]]
    original_count: int
    capped_count: int
    group_column: str
    cap: int
    _group_sizes: Dict[str, int] = field(default_factory=dict, repr=False)

    @property
    def removed_count(self) -> int:
        return self.original_count - self.capped_count

    @property
    def group_sizes(self) -> Dict[str, int]:
        return dict(self._group_sizes)


def _validate(rows: List[Dict[str, str]], column: str, cap: int) -> None:
    if cap < 1:
        raise CapperError(f"cap must be >= 1, got {cap}")
    if rows and column not in rows[0]:
        raise CapperError(f"column '{column}' not found in headers")


def cap_rows(
    rows: List[Dict[str, str]],
    column: str,
    cap: int,
) -> CapResult:
    """Return at most *cap* rows per unique value of *column*."""
    _validate(rows, column, cap)

    counts: Dict[str, int] = {}
    kept: List[Dict[str, str]] = []

    for row in rows:
        key = row[column]
        counts[key] = counts.get(key, 0) + 1
        if counts[key] <= cap:
            kept.append(row)

    return CapResult(
        rows=kept,
        original_count=len(rows),
        capped_count=len(kept),
        group_column=column,
        cap=cap,
        _group_sizes=counts,
    )
