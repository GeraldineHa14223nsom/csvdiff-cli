"""Zip (column-wise merge) two CSV datasets into a single row stream."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Sequence


class ZipperError(Exception):
    def __str__(self) -> str:
        return f"ZipperError: {self.args[0]}"


@dataclass
class ZipResult:
    headers: List[str]
    rows: List[Dict[str, str]]
    left_row_count: int
    right_row_count: int

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def column_count(self) -> int:
        return len(self.headers)


def _validate(
    left_headers: Sequence[str],
    right_headers: Sequence[str],
    left_prefix: str,
    right_prefix: str,
) -> None:
    if not left_headers:
        raise ZipperError("left CSV has no columns")
    if not right_headers:
        raise ZipperError("right CSV has no columns")
    if left_prefix == right_prefix:
        overlap = set(left_headers) & set(right_headers)
        if overlap:
            raise ZipperError(
                f"column name collision with identical prefixes: {sorted(overlap)}"
            )


def zip_rows(
    left_rows: List[Dict[str, str]],
    right_rows: List[Dict[str, str]],
    left_prefix: str = "",
    right_prefix: str = "",
    fill: str = "",
) -> ZipResult:
    """Merge two row lists column-wise (like Python's zip, but for CSV rows).

    Rows are paired by position.  If one side is shorter the missing values
    are filled with *fill*.  Column names are optionally prefixed to avoid
    collisions.
    """
    left_headers: List[str] = list(left_rows[0].keys()) if left_rows else []
    right_headers: List[str] = list(right_rows[0].keys()) if right_rows else []

    _validate(left_headers, right_headers, left_prefix, right_prefix)

    def _prefix(name: str, prefix: str) -> str:
        return f"{prefix}{name}" if prefix else name

    merged_headers = [
        _prefix(h, left_prefix) for h in left_headers
    ] + [
        _prefix(h, right_prefix) for h in right_headers
    ]

    length = max(len(left_rows), len(right_rows))
    merged: List[Dict[str, str]] = []

    for i in range(length):
        row: Dict[str, str] = {}
        if i < len(left_rows):
            for h in left_headers:
                row[_prefix(h, left_prefix)] = left_rows[i].get(h, fill)
        else:
            for h in left_headers:
                row[_prefix(h, left_prefix)] = fill
        if i < len(right_rows):
            for h in right_headers:
                row[_prefix(h, right_prefix)] = right_rows[i].get(h, fill)
        else:
            for h in right_headers:
                row[_prefix(h, right_prefix)] = fill
        merged.append(row)

    return ZipResult(
        headers=merged_headers,
        rows=merged,
        left_row_count=len(left_rows),
        right_row_count=len(right_rows),
    )
