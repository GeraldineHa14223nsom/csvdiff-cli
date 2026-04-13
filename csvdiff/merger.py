"""Merge two CSV files using a configurable strategy."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from csvdiff.core import DiffResult, _make_key


class MergeError(Exception):
    """Raised when a merge cannot be completed."""

    def __str__(self) -> str:  # pragma: no cover
        return f"MergeError: {self.args[0]}"


@dataclass
class MergeResult:
    rows: List[Dict[str, str]] = field(default_factory=list)
    conflicts: List[Tuple[Dict[str, str], Dict[str, str]]] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0


def merge(
    diff: DiffResult,
    keys: List[str],
    strategy: str = "ours",
    base: Optional[List[Dict[str, str]]] = None,
) -> MergeResult:
    """Merge diff result back into a unified row list.

    strategy:
      - "ours"   : keep left (old) value on conflict
      - "theirs" : keep right (new) value on conflict
      - "raise"  : raise MergeError on any conflict
    """
    if strategy not in ("ours", "theirs", "raise"):
        raise MergeError(f"Unknown merge strategy: {strategy!r}")

    rows: Dict[str, Dict[str, str]] = {}

    for row in (base or []):
        k = _make_key(row, keys)
        rows[k] = dict(row)

    for row in diff.added:
        k = _make_key(row, keys)
        rows[k] = dict(row)

    removed_keys = {_make_key(r, keys) for r in diff.removed}
    for k in removed_keys:
        rows.pop(k, None)

    conflicts: List[Tuple[Dict[str, str], Dict[str, str]]] = []
    for old, new in diff.modified:
        k = _make_key(new, keys)
        if strategy == "raise":
            raise MergeError(
                f"Conflict on key {k}: cannot auto-resolve with strategy 'raise'"
            )
        elif strategy == "ours":
            conflicts.append((old, new))
            rows[k] = dict(old)
        else:  # theirs
            conflicts.append((old, new))
            rows[k] = dict(new)

    return MergeResult(rows=list(rows.values()), conflicts=conflicts)
