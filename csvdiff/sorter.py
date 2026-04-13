"""Sorting utilities for CSV diff rows and results."""

from typing import List, Optional
from csvdiff.core import DiffResult


class SortError(Exception):
    """Raised when a sort column is invalid."""
    pass


DIRECTIONS = {"asc", "desc"}


def _validate_sort_column(column: str, available: List[str]) -> None:
    if column not in available:
        raise SortError(
            f"Sort column '{column}' not found in columns: {available}"
        )


def sort_rows(
    rows: List[dict],
    key: str,
    direction: str = "asc",
    available: Optional[List[str]] = None,
) -> List[dict]:
    """Sort a list of row dicts by *key* in *direction* order.

    Parameters
    ----------
    rows:      list of row dicts to sort
    key:       column name to sort by
    direction: 'asc' (default) or 'desc'
    available: optional explicit list of valid column names for validation
    """
    if direction not in DIRECTIONS:
        raise SortError(f"direction must be one of {DIRECTIONS}, got '{direction}'")

    if available is not None:
        _validate_sort_column(key, available)
    elif rows:
        _validate_sort_column(key, list(rows[0].keys()))

    reverse = direction == "desc"
    return sorted(rows, key=lambda r: r.get(key, ""), reverse=reverse)


def sort_result(
    result: DiffResult,
    key: str,
    direction: str = "asc",
) -> DiffResult:
    """Return a new DiffResult with all row lists sorted by *key*."""
    available: Optional[List[str]] = None
    all_rows = result.added + result.removed + [
        r["before"] for r in result.modified
    ]
    if all_rows:
        available = list(all_rows[0].keys())

    def _sort(rows: List[dict]) -> List[dict]:
        if not rows:
            return rows
        return sort_rows(rows, key, direction, available)

    modified_sorted = sorted(
        result.modified,
        key=lambda r: r["before"].get(key, ""),
        reverse=(direction == "desc"),
    )

    return DiffResult(
        added=_sort(result.added),
        removed=_sort(result.removed),
        modified=modified_sorted,
        unchanged=_sort(result.unchanged),
    )
