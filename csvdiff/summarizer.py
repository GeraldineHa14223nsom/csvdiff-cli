"""Summarize CSV data by computing per-column statistics in one pass."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class SummarizerError(Exception):
    def __str__(self) -> str:
        return f"SummarizerError: {self.args[0]}"


@dataclass
class ColumnSummary:
    column: str
    count: int
    non_empty: int
    numeric_count: int
    min_value: Optional[float]
    max_value: Optional[float]
    mean_value: Optional[float]

    @property
    def empty_count(self) -> int:
        return self.count - self.non_empty

    @property
    def fill_rate(self) -> float:
        return self.non_empty / self.count if self.count else 0.0


@dataclass
class SummaryResult:
    columns: List[ColumnSummary]
    row_count: int
    _index: Dict[str, ColumnSummary] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self._index = {c.column: c for c in self.columns}

    def get(self, column: str) -> Optional[ColumnSummary]:
        return self._index.get(column)


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def summarize(rows: List[Dict[str, str]], columns: Optional[List[str]] = None) -> SummaryResult:
    """Compute per-column summary statistics for *rows*.

    Args:
        rows: list of row dicts (as produced by csv.DictReader).
        columns: optional subset of columns to summarise; defaults to all.

    Returns:
        SummaryResult containing one ColumnSummary per column.

    Raises:
        SummarizerError: if *columns* contains a name absent from the data.
    """
    if not rows:
        return SummaryResult(columns=[], row_count=0)

    all_columns = list(rows[0].keys())
    target = columns if columns is not None else all_columns

    unknown = [c for c in target if c not in all_columns]
    if unknown:
        raise SummarizerError(f"Unknown columns: {unknown}")

    accumulators: Dict[str, Dict] = {
        col: {"count": 0, "non_empty": 0, "nums": [], "min": None, "max": None}
        for col in target
    }

    for row in rows:
        for col in target:
            acc = accumulators[col]
            val = row.get(col, "")
            acc["count"] += 1
            if val.strip():
                acc["non_empty"] += 1
            num = _to_float(val)
            if num is not None:
                acc["nums"].append(num)
                acc["min"] = min(acc["min"], num) if acc["min"] is not None else num
                acc["max"] = max(acc["max"], num) if acc["max"] is not None else num

    summaries = []
    for col in target:
        acc = accumulators[col]
        nums = acc["nums"]
        mean = sum(nums) / len(nums) if nums else None
        summaries.append(ColumnSummary(
            column=col,
            count=acc["count"],
            non_empty=acc["non_empty"],
            numeric_count=len(nums),
            min_value=acc["min"],
            max_value=acc["max"],
            mean_value=mean,
        ))

    return SummaryResult(columns=summaries, row_count=len(rows))
