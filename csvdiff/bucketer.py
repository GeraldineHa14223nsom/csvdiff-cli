"""Bucket rows into named groups based on value ranges for a numeric column."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class BucketerError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class BucketResult:
    headers: List[str]
    rows: List[dict]
    bucket_column: str
    label_column: str
    bucket_counts: Dict[str, int] = field(default_factory=dict)

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def bucket_count(self) -> int:
        return len(self.bucket_counts)


def _validate(rows: List[dict], column: str, buckets: List[tuple]) -> None:
    if not rows:
        return
    if column not in rows[0]:
        raise BucketerError(f"Column '{column}' not found in headers.")
    if not buckets:
        raise BucketerError("At least one bucket must be provided.")
    for item in buckets:
        if len(item) != 3:
            raise BucketerError(
                "Each bucket must be a (label, low, high) tuple."
            )
        label, low, high = item
        if low >= high:
            raise BucketerError(
                f"Bucket '{label}': low ({low}) must be less than high ({high})."
            )


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def bucket_rows(
    rows: List[dict],
    column: str,
    buckets: List[tuple],
    label_column: str = "bucket",
    default_label: str = "other",
) -> BucketResult:
    """Assign each row a bucket label based on the value in *column*.

    *buckets* is a list of ``(label, low, high)`` tuples where the range is
    ``[low, high)`` (inclusive low, exclusive high).
    """
    _validate(rows, column, buckets)

    out_rows: List[dict] = []
    counts: Dict[str, int] = {}

    for row in rows:
        val = _to_float(row.get(column, ""))
        assigned = default_label
        if val is not None:
            for label, low, high in buckets:
                if low <= val < high:
                    assigned = label
                    break
        new_row = dict(row)
        new_row[label_column] = assigned
        counts[assigned] = counts.get(assigned, 0) + 1
        out_rows.append(new_row)

    headers = list(rows[0].keys()) + [label_column] if rows else [label_column]
    return BucketResult(
        headers=headers,
        rows=out_rows,
        bucket_column=column,
        label_column=label_column,
        bucket_counts=counts,
    )
