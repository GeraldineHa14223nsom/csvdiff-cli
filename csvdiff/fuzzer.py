"""Fuzzy string matching between two CSV files on a key column."""
from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Dict, List, Optional


class FuzzerError(Exception):
    def __str__(self) -> str:
        return f"FuzzerError: {self.args[0]}"


@dataclass
class FuzzyMatch:
    left_key: str
    right_key: str
    score: float
    left_row: Dict[str, str]
    right_row: Dict[str, str]


@dataclass
class FuzzyResult:
    matches: List[FuzzyMatch] = field(default_factory=list)
    unmatched_left: List[Dict[str, str]] = field(default_factory=list)
    unmatched_right: List[Dict[str, str]] = field(default_factory=list)

    @property
    def match_count(self) -> int:
        return len(self.matches)

    @property
    def mean_score(self) -> Optional[float]:
        if not self.matches:
            return None
        return sum(m.score for m in self.matches) / len(self.matches)


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _validate(rows: List[Dict[str, str]], key: str, side: str) -> None:
    if not rows:
        return
    if key not in rows[0]:
        raise FuzzerError(f"Key column '{key}' not found in {side} rows")


def fuzzy_match(
    left_rows: List[Dict[str, str]],
    right_rows: List[Dict[str, str]],
    key: str,
    threshold: float = 0.8,
) -> FuzzyResult:
    """Match rows from left to right using fuzzy key similarity."""
    if not 0.0 <= threshold <= 1.0:
        raise FuzzerError(f"Threshold must be between 0.0 and 1.0, got {threshold}")
    _validate(left_rows, key, "left")
    _validate(right_rows, key, "right")

    result = FuzzyResult()
    used_right: set = set()

    for left_row in left_rows:
        left_key = left_row[key]
        best_score = -1.0
        best_idx: Optional[int] = None

        for idx, right_row in enumerate(right_rows):
            if idx in used_right:
                continue
            score = _similarity(left_key, right_row[key])
            if score > best_score:
                best_score = score
                best_idx = idx

        if best_idx is not None and best_score >= threshold:
            result.matches.append(
                FuzzyMatch(
                    left_key=left_key,
                    right_key=right_rows[best_idx][key],
                    score=round(best_score, 4),
                    left_row=left_row,
                    right_row=right_rows[best_idx],
                )
            )
            used_right.add(best_idx)
        else:
            result.unmatched_left.append(left_row)

    for idx, right_row in enumerate(right_rows):
        if idx not in used_right:
            result.unmatched_right.append(right_row)

    return result
