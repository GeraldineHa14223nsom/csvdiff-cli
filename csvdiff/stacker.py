"""Stack (vertically concatenate) multiple CSV datasets."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Sequence


class StackerError(Exception):
    def __str__(self) -> str:  # pragma: no cover
        return f"StackerError: {self.args[0]}"


@dataclass
class StackResult:
    headers: List[str]
    rows: List[Dict[str, str]]
    source_counts: List[int] = field(default_factory=list)

    @property
    def total_rows(self) -> int:
        return len(self.rows)

    @property
    def source_count(self) -> int:
        return len(self.source_counts)


def _validate_headers(
    headers_list: List[List[str]], strict: bool
) -> List[str]:
    if not headers_list:
        raise StackerError("No datasets provided to stack.")
    base = headers_list[0]
    for i, h in enumerate(headers_list[1:], start=2):
        if strict and set(h) != set(base):
            raise StackerError(
                f"Dataset {i} has different columns: {h} vs {base}"
            )
    if strict:
        return list(base)
    # union of all columns, preserving first-seen order
    seen: Dict[str, None] = {}
    for h in headers_list:
        for col in h:
            seen.setdefault(col, None)
    return list(seen)


def stack(
    datasets: Sequence[List[Dict[str, str]]],
    headers_list: Sequence[List[str]],
    *,
    strict: bool = True,
    fill_value: str = "",
) -> StackResult:
    """Stack datasets vertically.

    Parameters
    ----------
    datasets:     sequence of row-lists (each row is a dict).
    headers_list: column names for each dataset.
    strict:       if True, raise when column sets differ.
    fill_value:   value used for missing columns in non-strict mode.
    """
    merged_headers = _validate_headers(list(headers_list), strict)
    all_rows: List[Dict[str, str]] = []
    counts: List[int] = []
    for rows in datasets:
        count = 0
        for row in rows:
            all_rows.append(
                {col: row.get(col, fill_value) for col in merged_headers}
            )
            count += 1
        counts.append(count)
    return StackResult(headers=merged_headers, rows=all_rows, source_counts=counts)
