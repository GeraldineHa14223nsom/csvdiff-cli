"""Column value clipping — clamp numeric values to [min, max] bounds."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional


class ClipperError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class ClipResult:
    rows: List[Dict[str, str]]
    column: str
    clipped_count: int
    original_count: int


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _validate(rows: List[Dict[str, str]], column: str) -> None:
    if not rows:
        return
    if column not in rows[0]:
        raise ClipperError(f"Column '{column}' not found in headers.")


def clip_column(
    rows: List[Dict[str, str]],
    column: str,
    low: Optional[float] = None,
    high: Optional[float] = None,
) -> ClipResult:
    """Clamp numeric values in *column* to [low, high]. Non-numeric cells are left unchanged."""
    if low is not None and high is not None and low > high:
        raise ClipperError(f"low ({low}) must be <= high ({high}).")
    _validate(rows, column)

    clipped = 0
    out: List[Dict[str, str]] = []
    for row in rows:
        new_row = dict(row)
        val = _to_float(row[column])
        if val is not None:
            original = val
            if low is not None and val < low:
                val = low
            if high is not None and val > high:
                val = high
            if val != original:
                clipped += 1
            # Preserve int-like formatting when possible
            new_row[column] = str(int(val)) if val == int(val) else str(val)
        out.append(new_row)

    return ClipResult(
        rows=out,
        column=column,
        clipped_count=clipped,
        original_count=len(rows),
    )
