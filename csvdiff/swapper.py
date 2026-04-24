"""Column value swapper — exchange values between two columns."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


class SwapperError(Exception):
    def __str__(self) -> str:  # pragma: no cover
        return self.args[0]


@dataclass
class SwapResult:
    rows: List[Dict[str, str]]
    col_a: str
    col_b: str
    row_count: int

    @property
    def swapped_count(self) -> int:
        """Number of rows where the two column values actually differed."""
        return sum(
            1 for r in self.rows if r.get(self.col_a) != r.get(self.col_b)
        )


def _validate(rows: List[Dict[str, str]], col_a: str, col_b: str) -> None:
    if not rows:
        return
    headers = set(rows[0].keys())
    missing = [c for c in (col_a, col_b) if c not in headers]
    if missing:
        raise SwapperError(
            f"Column(s) not found: {', '.join(missing)}"
        )
    if col_a == col_b:
        raise SwapperError("col_a and col_b must be different columns")


def swap_columns(
    rows: List[Dict[str, str]],
    col_a: str,
    col_b: str,
) -> SwapResult:
    """Return a new list of rows with values in *col_a* and *col_b* exchanged."""
    _validate(rows, col_a, col_b)
    swapped: List[Dict[str, str]] = []
    for row in rows:
        new_row = dict(row)
        new_row[col_a], new_row[col_b] = row[col_b], row[col_a]
        swapped.append(new_row)
    return SwapResult(
        rows=swapped,
        col_a=col_a,
        col_b=col_b,
        row_count=len(swapped),
    )
