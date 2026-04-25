"""Column-width shrinker: truncate string values in chosen columns to a max length."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


class ShrinkerError(Exception):
    def __str__(self) -> str:
        return f"ShrinkerError: {self.args[0]}"


@dataclass
class ShrinkResult:
    headers: List[str]
    rows: List[Dict[str, str]]
    column: str
    max_length: int
    truncated_count: int = field(default=0)

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def truncation_rate(self) -> float:
        if self.row_count == 0:
            return 0.0
        return self.truncated_count / self.row_count


def _validate(headers: List[str], column: str, max_length: int) -> None:
    if column not in headers:
        raise ShrinkerError(f"column '{column}' not found in headers: {headers}")
    if max_length < 1:
        raise ShrinkerError(f"max_length must be >= 1, got {max_length}")


def shrink(
    rows: List[Dict[str, str]],
    column: str,
    max_length: int,
    ellipsis_str: str = "...",
) -> ShrinkResult:
    """Truncate values in *column* to *max_length* characters.

    When a value is truncated the *ellipsis_str* is appended (the result
    total length is still capped at *max_length*).
    """
    if not rows:
        return ShrinkResult(
            headers=[], rows=[], column=column,
            max_length=max_length, truncated_count=0,
        )

    headers = list(rows[0].keys())
    _validate(headers, column, max_length)

    ell_len = len(ellipsis_str)
    out: List[Dict[str, str]] = []
    truncated = 0

    for row in rows:
        new_row = dict(row)
        val = row[column]
        if len(val) > max_length:
            if max_length <= ell_len:
                new_row[column] = ellipsis_str[:max_length]
            else:
                new_row[column] = val[: max_length - ell_len] + ellipsis_str
            truncated += 1
        out.append(new_row)

    return ShrinkResult(
        headers=headers,
        rows=out,
        column=column,
        max_length=max_length,
        truncated_count=truncated,
    )
