"""Group CSV rows by one or more columns and compute per-group aggregates."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Sequence


class GrouperError(Exception):
    def __str__(self) -> str:  # pragma: no cover
        return self.args[0]


@dataclass
class GroupResult:
    group_keys: List[str]
    groups: Dict[tuple, List[dict]] = field(default_factory=dict)

    def group_count(self) -> int:
        return len(self.groups)

    def row_count(self) -> int:
        return sum(len(rows) for rows in self.groups.values())

    def to_summary_rows(self, agg_column: str, agg_func: str) -> List[dict]:
        """Return one summary row per group with an aggregated value."""
        from csvdiff.aggregator import aggregate_column  # local to avoid circular

        rows: List[dict] = []
        for key_tuple, group_rows in self.groups.items():
            from csvdiff.aggregator import AggregateResult
            agg: AggregateResult = aggregate_column(group_rows, agg_column, agg_func)
            summary = dict(zip(self.group_keys, key_tuple))
            summary[f"{agg_func}_{agg_column}"] = str(agg.value)
            rows.append(summary)
        return rows


def group_rows(
    rows: List[dict],
    keys: Sequence[str],
) -> GroupResult:
    """Partition *rows* into groups defined by *keys*."""
    if not keys:
        raise GrouperError("At least one group key must be specified.")

    if rows:
        missing = [k for k in keys if k not in rows[0]]
        if missing:
            raise GrouperError(
                f"Group key(s) not found in data: {', '.join(missing)}"
            )

    buckets: Dict[tuple, List[dict]] = defaultdict(list)
    for row in rows:
        bucket_key = tuple(row.get(k, "") for k in keys)
        buckets[bucket_key].append(row)

    return GroupResult(group_keys=list(keys), groups=dict(buckets))
