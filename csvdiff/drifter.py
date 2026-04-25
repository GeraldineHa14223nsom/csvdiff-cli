"""Detect schema drift between two CSV files (header changes)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence


class DrifterError(Exception):
    def __str__(self) -> str:  # pragma: no cover
        return super().__str__()


@dataclass
class DriftResult:
    left_headers: List[str]
    right_headers: List[str]
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    reordered: bool = False

    @property
    def has_drift(self) -> bool:
        return bool(self.added or self.removed or self.reordered)

    @property
    def column_count_left(self) -> int:
        return len(self.left_headers)

    @property
    def column_count_right(self) -> int:
        return len(self.right_headers)


def _validate(left: Sequence[str], right: Sequence[str]) -> None:
    if not left:
        raise DrifterError("Left header list must not be empty.")
    if not right:
        raise DrifterError("Right header list must not be empty.")


def detect_drift(left: Sequence[str], right: Sequence[str]) -> DriftResult:
    """Compare two header sequences and return a DriftResult describing changes."""
    _validate(left, right)

    left_set = set(left)
    right_set = set(right)

    added = [c for c in right if c not in left_set]
    removed = [c for c in left if c not in right_set]

    common_left = [c for c in left if c in right_set]
    common_right = [c for c in right if c in left_set]
    reordered = common_left != common_right

    return DriftResult(
        left_headers=list(left),
        right_headers=list(right),
        added=added,
        removed=removed,
        reordered=reordered,
    )
