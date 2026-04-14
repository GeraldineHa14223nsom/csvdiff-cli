"""Split a CSV file into multiple chunks by row count or column value."""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class SplitterError(Exception):
    def __str__(self) -> str:
        return f"SplitterError: {self.args[0]}"


@dataclass
class SplitResult:
    chunks: Dict[str, List[dict]] = field(default_factory=dict)

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)

    @property
    def total_rows(self) -> int:
        return sum(len(rows) for rows in self.chunks.values())


def split_by_count(rows: List[dict], chunk_size: int) -> SplitResult:
    """Split rows into chunks of at most *chunk_size* rows each."""
    if chunk_size < 1:
        raise SplitterError("chunk_size must be >= 1")
    if not rows:
        return SplitResult()
    chunks: Dict[str, List[dict]] = {}
    for i in range(0, len(rows), chunk_size):
        key = str(i // chunk_size + 1)
        chunks[key] = rows[i : i + chunk_size]
    return SplitResult(chunks=chunks)


def split_by_column(rows: List[dict], column: str) -> SplitResult:
    """Split rows into groups keyed by the distinct values of *column*."""
    if not rows:
        return SplitResult()
    if column not in rows[0]:
        raise SplitterError(f"Column '{column}' not found in CSV headers")
    chunks: Dict[str, List[dict]] = {}
    for row in rows:
        key = row[column]
        chunks.setdefault(key, []).append(row)
    return SplitResult(chunks=chunks)


def chunk_to_csv(rows: List[dict]) -> str:
    """Serialise a list of row dicts back to a CSV string."""
    if not rows:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()
