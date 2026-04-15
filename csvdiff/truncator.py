"""Truncate CSV rows to a maximum number of rows from the top or bottom."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


class TruncatorError(Exception):
    def __str__(self) -> str:
        return f"TruncatorError: {self.args[0]}"


@dataclass
class TruncateResult:
    rows: List[Dict[str, str]]
    original_count: int
    truncated_count: int

    @property
    def removed_count(self) -> int:
        return self.original_count - self.truncated_count


def _validate(rows: List[Dict[str, str]], n: int, mode: str) -> None:
    if n < 0:
        raise TruncatorError(f"n must be non-negative, got {n}")
    if mode not in ("head", "tail"):
        raise TruncatorError(f"mode must be 'head' or 'tail', got {mode!r}")


def truncate(rows: List[Dict[str, str]], n: int, mode: str = "head") -> TruncateResult:
    """Return the first (head) or last (tail) *n* rows.

    Parameters
    ----------
    rows:
        Input rows as a list of dicts.
    n:
        Maximum number of rows to keep.
    mode:
        ``'head'`` keeps the first *n* rows; ``'tail'`` keeps the last *n*.

    Returns
    -------
    TruncateResult
    """
    _validate(rows, n, mode)
    original = len(rows)
    if mode == "head":
        kept = rows[:n]
    else:
        kept = rows[-n:] if n > 0 else []
    return TruncateResult(
        rows=kept,
        original_count=original,
        truncated_count=len(kept),
    )
