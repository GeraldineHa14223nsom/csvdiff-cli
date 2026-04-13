"""High-level pipeline that wires filtering into the diff workflow."""
from __future__ import annotations

import csv
import io
from typing import Sequence

from csvdiff.core import diff, DiffResult
from csvdiff.filters import exclude_rows, filter_columns, filter_rows


def _read_rows(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def run(
    path_a: str,
    path_b: str,
    keys: Sequence[str],
    *,
    include_columns: list[str] | None = None,
    exclude_columns: list[str] | None = None,
    filter_column: str | None = None,
    filter_values: list[str] | None = None,
    exclude_column: str | None = None,
    exclude_values: list[str] | None = None,
) -> DiffResult:
    """Load two CSV files, apply filters, then return a :class:`DiffResult`."""
    rows_a = _read_rows(path_a)
    rows_b = _read_rows(path_b)

    # Row-level filters applied to both sides consistently
    if filter_column and filter_values:
        rows_a = filter_rows(rows_a, filter_column, filter_values)
        rows_b = filter_rows(rows_b, filter_column, filter_values)

    if exclude_column and exclude_values:
        rows_a = exclude_rows(rows_a, exclude_column, exclude_values)
        rows_b = exclude_rows(rows_b, exclude_column, exclude_values)

    # Column projection
    if include_columns or exclude_columns:
        rows_a = filter_columns(rows_a, include=include_columns, exclude=exclude_columns)
        rows_b = filter_columns(rows_b, include=include_columns, exclude=exclude_columns)

    return diff(rows_a, rows_b, keys=list(keys))
