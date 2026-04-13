"""Statistics computed from a DiffResult."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from csvdiff.core import DiffResult


@dataclass
class DiffStats:
    added: int
    removed: int
    modified: int
    unchanged: int

    @classmethod
    def from_result(cls, result: DiffResult) -> "DiffStats":
        return cls(
            added=len(result.added),
            removed=len(result.removed),
            modified=len(result.modified),
            unchanged=len(result.unchanged),
        )


def total_changes(stats: DiffStats) -> int:
    """Return the number of rows that were added, removed, or modified."""
    return stats.added + stats.removed + stats.modified


def total_rows(stats: DiffStats) -> int:
    """Return the total number of rows across both files (union count)."""
    return stats.added + stats.removed + stats.modified + stats.unchanged


def change_rate(stats: DiffStats) -> float:
    """Return the fraction of rows that changed (0.0 – 1.0)."""
    total = total_rows(stats)
    if total == 0:
        return 0.0
    return total_changes(stats) / total


def as_dict(stats: DiffStats) -> dict[str, Any]:
    """Serialise *stats* to a plain dictionary suitable for JSON output."""
    return {
        "added": stats.added,
        "removed": stats.removed,
        "modified": stats.modified,
        "unchanged": stats.unchanged,
        "total_changes": total_changes(stats),
        "total_rows": total_rows(stats),
        "change_rate": change_rate(stats),
        "change_rate_pct": round(change_rate(stats) * 100, 4),
    }


def format_stats(stats: DiffStats) -> str:
    """Return a compact one-line summary string."""
    d = as_dict(stats)
    return (
        f"+{d['added']} added, -{d['removed']} removed, "
        f"~{d['modified']} modified, {d['unchanged']} unchanged "
        f"({d['change_rate_pct']:.1f}% changed)"
    )
