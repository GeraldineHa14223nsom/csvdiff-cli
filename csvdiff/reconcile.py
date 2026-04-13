"""Reconciliation helpers: apply a DiffResult back to a base CSV."""
from __future__ import annotations

import csv
import io
from typing import Dict, List, Tuple

from csvdiff.core import DiffResult


def reconcile(
    diff: DiffResult,
    base_rows: List[Dict],
    key_cols: List[str],
) -> List[Dict]:
    """Return a new list of rows that reflects all changes in *diff*.

    Strategy:
      - Start from *base_rows* (the "old" side).
      - Remove rows whose key appears in ``diff.removed``.
      - Apply updated values for rows whose key appears in ``diff.modified``.
      - Append rows from ``diff.added``.
    The returned list preserves the original row order for unchanged / modified
    rows, then appends additions at the end.
    """
    def _key(row: Dict) -> Tuple:
        return tuple(row.get(c, "") for c in key_cols)

    removed_keys = {_key(r) for r in diff.removed}
    modified_map = {_key(entry["new"]): entry["new"] for entry in diff.modified}

    result: List[Dict] = []
    for row in base_rows:
        k = _key(row)
        if k in removed_keys:
            continue
        if k in modified_map:
            result.append(modified_map[k])
        else:
            result.append(row)

    for row in diff.added:
        result.append(row)

    return result


def reconcile_to_csv(
    diff: DiffResult,
    base_rows: List[Dict],
    key_cols: List[str],
    fieldnames: List[str] | None = None,
) -> str:
    """Reconcile and serialise the result as a CSV string."""
    rows = reconcile(diff, base_rows, key_cols)
    if not rows:
        return ""
    fields = fieldnames or list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=fields, lineterminator="\n", extrasaction="ignore"
    )
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()
