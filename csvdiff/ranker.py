"""Rank rows by a numeric column."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional


class RankerError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class RankResult:
    rows: List[Dict[str, str]]
    column: str
    rank_column: str
    ascending: bool

    @property
    def ranked_count(self) -> int:
        return len(self.rows)


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        raise RankerError(f"Non-numeric value cannot be ranked: {value!r}")


def _validate(rows: List[Dict[str, str]], column: str) -> None:
    if not rows:
        return
    if column not in rows[0]:
        raise RankerError(f"Column {column!r} not found in headers")


def rank_rows(
    rows: List[Dict[str, str]],
    column: str,
    *,
    ascending: bool = True,
    rank_column: str = "rank",
    method: str = "dense",
) -> RankResult:
    """Add a rank column based on *column* values.

    method: 'dense' (no gaps) or 'standard' (gaps on ties).
    """
    if method not in ("dense", "standard"):
        raise RankerError(f"Unknown rank method {method!r}; use 'dense' or 'standard'")
    _validate(rows, column)
    if not rows:
        return RankResult(rows=[], column=column, rank_column=rank_column, ascending=ascending)

    scored = [(i, _to_float(r[column])) for i, r in enumerate(rows)]
    scored.sort(key=lambda x: x[1], reverse=not ascending)

    rank_map: Dict[int, int] = {}
    if method == "dense":
        current_rank = 1
        prev_val: Optional[float] = None
        for idx, (orig_i, val) in enumerate(scored):
            if val != prev_val:
                current_rank = idx + 1 if method == "standard" else current_rank if prev_val is None else current_rank + 1
                prev_val = val
            rank_map[orig_i] = current_rank
    else:
        for pos, (orig_i, _) in enumerate(scored, start=1):
            rank_map[orig_i] = pos

    result_rows = []
    for i, row in enumerate(rows):
        result_rows.append({**row, rank_column: str(rank_map[i])})

    return RankResult(rows=result_rows, column=column, rank_column=rank_column, ascending=ascending)
