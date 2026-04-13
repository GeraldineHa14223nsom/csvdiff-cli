"""Join two CSV datasets on a common key column."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence


class JoinError(Exception):
    def __str__(self) -> str:
        return f"JoinError: {self.args[0]}"


@dataclass
class JoinResult:
    rows: List[Dict[str, str]] = field(default_factory=list)
    left_only: List[Dict[str, str]] = field(default_factory=list)
    right_only: List[Dict[str, str]] = field(default_factory=list)
    join_type: str = "inner"


def _index(rows: List[Dict[str, str]], key: str) -> Dict[str, Dict[str, str]]:
    if not rows:
        return {}
    if key not in rows[0]:
        raise JoinError(f"Key column '{key}' not found in rows")
    return {row[key]: row for row in rows}


def join(
    left: List[Dict[str, str]],
    right: List[Dict[str, str]],
    key: str,
    how: str = "inner",
    suffixes: Sequence[str] = ("_left", "_right"),
) -> JoinResult:
    """Join *left* and *right* on *key*.

    *how* may be ``'inner'``, ``'left'``, ``'right'``, or ``'outer'``.
    Conflicting non-key columns are renamed with *suffixes*.
    """
    if how not in {"inner", "left", "right", "outer"}:
        raise JoinError(f"Unknown join type '{how}'; expected inner/left/right/outer")

    left_idx = _index(left, key)
    right_idx = _index(right, key)

    left_only: List[Dict[str, str]] = []
    right_only: List[Dict[str, str]] = []
    joined: List[Dict[str, str]] = []

    all_keys = list(left_idx) + [k for k in right_idx if k not in left_idx]

    for k in all_keys:
        in_left = k in left_idx
        in_right = k in right_idx

        if in_left and in_right:
            merged = {key: k}
            l_row = {c: v for c, v in left_idx[k].items() if c != key}
            r_row = {c: v for c, v in right_idx[k].items() if c != key}
            shared = set(l_row) & set(r_row)
            for col in l_row:
                merged[col + suffixes[0] if col in shared else col] = l_row[col]
            for col in r_row:
                merged[col + suffixes[1] if col in shared else col] = r_row[col]
            joined.append(merged)
        elif in_left and how in {"left", "outer"}:
            left_only.append(left_idx[k])
        elif in_right and how in {"right", "outer"}:
            right_only.append(right_idx[k])

    return JoinResult(rows=joined, left_only=left_only, right_only=right_only, join_type=how)
