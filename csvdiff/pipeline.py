"""High-level pipeline: read -> filter -> transform -> diff."""

from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional

from csvdiff.core import DiffResult, diff
from csvdiff.filters import exclude_rows, filter_columns, filter_rows
from csvdiff.transform import apply_transforms, rename_columns


def _read_rows(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def run(
    left_path: Path,
    right_path: Path,
    keys: List[str],
    *,
    include_columns: Optional[List[str]] = None,
    exclude_columns: Optional[List[str]] = None,
    filter_expr: Optional[str] = None,
    exclude_expr: Optional[str] = None,
    transforms: Optional[Dict[str, str]] = None,
    renames: Optional[Dict[str, str]] = None,
) -> DiffResult:
    """Read two CSV files, apply optional filters/transforms, and diff them.

    Args:
        left_path: Path to the 'old' CSV.
        right_path: Path to the 'new' CSV.
        keys: Column names that uniquely identify a row.
        include_columns: If given, keep only these columns.
        exclude_columns: If given, drop these columns.
        filter_expr: Python expression string to keep matching rows.
        exclude_expr: Python expression string to drop matching rows.
        transforms: Mapping of column -> transform name to apply.
        renames: Mapping of old column name -> new column name.

    Returns:
        A :class:`~csvdiff.core.DiffResult`.
    """
    left = _read_rows(left_path)
    right = _read_rows(right_path)

    for rows in (left, right):
        if include_columns or exclude_columns:
            rows[:] = filter_columns(
                rows,
                include=include_columns,
                exclude=exclude_columns,
            )
        if filter_expr:
            rows[:] = filter_rows(rows, filter_expr)
        if exclude_expr:
            rows[:] = exclude_rows(rows, exclude_expr)
        if transforms:
            rows[:] = apply_transforms(rows, transforms)
        if renames:
            rows[:] = rename_columns(rows, renames)

    # Adjust key names if they were renamed
    effective_keys = [
        (renames or {}).get(k, k) for k in keys
    ]

    return diff(left, right, keys=effective_keys)
