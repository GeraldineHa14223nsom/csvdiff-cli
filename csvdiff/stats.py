"""Statistics and summary reporting for CSV diff results."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from csvdiff.core import DiffResult


@dataclass(frozen=True)
class DiffStats:
    """Aggregated statistics derived from a DiffResult."""

    added: int
    removed: int
    modified: int
    unchanged: int

    @property
    def total_changes(self) -> int:
        return self.added + self.removed + self.modified

    @property
    def total_rows(self) -> int:
        return self.added + self.removed + self.modified + self.unchanged

    @property
    def change_rate(self) -> float:
        """Fraction of rows that changed (0.0 – 1.0)."""
        if self.total_rows == 0:
            return 0.0
        return self.total_changes / self.total_rows

    def as_dict(self) -> dict:
        return {
            "added": self.added,
            "removed": self.removed,
            "modified": self.modified,
            "unchanged": self.unchanged,
            "total_changes": self.total_changes,
            "total_rows": self.total_rows,
            "change_rate": round(self.change_rate, 4),
        }


def compute_stats(result: "DiffResult") -> DiffStats:
    """Compute statistics from a DiffResult."""
    return DiffStats(
        added=len(result.added),
        removed=len(result.removed),
        modified=len(result.modified),
        unchanged=len(result.unchanged),
    )


def format_stats_text(stats: DiffStats) -> str:
    """Return a human-readable summary string."""
    lines = [
        f"Added   : {stats.added}",
        f"Removed : {stats.removed}",
        f"Modified: {stats.modified}",
        f"Unchanged: {stats.unchanged}",
        f"Total changes: {stats.total_changes} / {stats.total_rows} rows "
        f"({stats.change_rate:.1%})",
    ]
    return "\n".join(lines)
