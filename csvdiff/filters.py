"""Column and row filtering utilities for csvdiff."""
from __future__ import annotations

from typing import Iterable


def filter_columns(
    rows: Iterable[dict],
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[dict]:
    """Return rows keeping only *include* columns or dropping *exclude* columns.

    *include* takes precedence over *exclude*. If neither is supplied the rows
    are returned unchanged.
    """
    rows = list(rows)
    if not rows:
        return rows

    if include is not None:
        unknown = set(include) - set(rows[0].keys())
        if unknown:
            raise ValueError(f"Unknown columns to include: {sorted(unknown)}")
        return [{col: row[col] for col in include} for row in rows]

    if exclude is not None:
        keep = [c for c in rows[0].keys() if c not in exclude]
        return [{col: row[col] for col in keep} for row in rows]

    return rows


def filter_rows(
    rows: Iterable[dict],
    column: str,
    values: Iterable[str],
) -> list[dict]:
    """Return only rows where *column* value is in *values*."""
    value_set = set(values)
    return [row for row in rows if row.get(column) in value_set]


def exclude_rows(
    rows: Iterable[dict],
    column: str,
    values: Iterable[str],
) -> list[dict]:
    """Return rows where *column* value is NOT in *values*."""
    value_set = set(values)
    return [row for row in rows if row.get(column) not in value_set]
