"""Column profiling: compute per-column statistics for a CSV dataset."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ColumnProfile:
    name: str
    count: int = 0
    non_empty: int = 0
    unique_values: int = 0
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    sample_values: List[str] = field(default_factory=list)

    @property
    def empty_count(self) -> int:
        return self.count - self.non_empty

    @property
    def fill_rate(self) -> float:
        return (self.non_empty / self.count) if self.count else 0.0


@dataclass
class ProfileResult:
    columns: List[str]
    profiles: Dict[str, ColumnProfile]


class ProfilerError(Exception):
    def __str__(self) -> str:
        return self.args[0]


MAX_SAMPLE = 5


def profile_rows(rows: List[Dict[str, str]], sample_size: int = MAX_SAMPLE) -> ProfileResult:
    """Profile each column in *rows*, returning a ProfileResult."""
    if not rows:
        return ProfileResult(columns=[], profiles={})

    columns = list(rows[0].keys())
    profiles: Dict[str, ColumnProfile] = {col: ColumnProfile(name=col) for col in columns}
    seen: Dict[str, set] = {col: set() for col in columns}

    for row in rows:
        for col in columns:
            val = row.get(col, "")
            p = profiles[col]
            p.count += 1
            length = len(val)
            if val.strip():
                p.non_empty += 1
            seen[col].add(val)
            p.min_length = length if p.min_length is None else min(p.min_length, length)
            p.max_length = length if p.max_length is None else max(p.max_length, length)
            if len(p.sample_values) < sample_size:
                p.sample_values.append(val)

    for col in columns:
        profiles[col].unique_values = len(seen[col])

    return ProfileResult(columns=columns, profiles=profiles)
