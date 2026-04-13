"""Deduplication utilities for CSV rows based on key columns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


class DeduplicatorError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class DedupeResult:
    unique: List[Dict] = field(default_factory=list)
    duplicates: List[Tuple[Dict, int]] = field(default_factory=list)  # (row, first_seen_index)

    @property
    def duplicate_count(self) -> int:
        return len(self.duplicates)

    @property
    def unique_count(self) -> int:
        return len(self.unique)


def _make_key(row: Dict, keys: List[str]) -> Tuple:
    try:
        return tuple(row[k] for k in keys)
    except KeyError as exc:
        raise DeduplicatorError(f"Key column {exc} not found in row: {row}") from exc


def deduplicate(rows: List[Dict], keys: List[str], keep: str = "first") -> DedupeResult:
    """Remove duplicate rows based on key columns.

    Args:
        rows: List of row dicts.
        keys: Column names forming the composite key.
        keep: 'first' keeps the earliest occurrence; 'last' keeps the latest.

    Returns:
        DedupeResult with unique rows and duplicates.
    """
    if keep not in ("first", "last"):
        raise DeduplicatorError(f"Invalid keep strategy '{keep}'; expected 'first' or 'last'.")

    seen: Dict[Tuple, int] = {}  # key -> index in unique list
    result = DedupeResult()

    for row in rows:
        k = _make_key(row, keys)
        if k not in seen:
            seen[k] = len(result.unique)
            result.unique.append(row)
        else:
            if keep == "last":
                original_index = seen[k]
                result.duplicates.append((result.unique[original_index], original_index))
                result.unique[original_index] = row
            else:
                result.duplicates.append((row, seen[k]))

    return result


def find_duplicate_keys(rows: List[Dict], keys: List[str]) -> Dict[Tuple, List[Dict]]:
    """Return a mapping of duplicate keys to all rows sharing that key."""
    groups: Dict[Tuple, List[Dict]] = {}
    for row in rows:
        k = _make_key(row, keys)
        groups.setdefault(k, []).append(row)
    return {k: v for k, v in groups.items() if len(v) > 1}
