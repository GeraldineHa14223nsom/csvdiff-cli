"""Row similarity scoring using configurable metrics."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Sequence


class ScorerError(Exception):
    def __str__(self) -> str:
        return f"ScorerError: {self.args[0]}"


@dataclass
class ScoreResult:
    rows: List[Dict[str, str]]
    score_column: str
    metric: str

    def scored_count(self) -> int:
        return len(self.rows)

    def mean_score(self) -> float:
        if not self.rows:
            return 0.0
        vals = [float(r[self.score_column]) for r in self.rows]
        return sum(vals) / len(vals)


def _validate(rows: List[Dict[str, str]], columns: Sequence[str]) -> None:
    if not columns:
        raise ScorerError("At least one column must be specified.")
    if rows:
        missing = [c for c in columns if c not in rows[0]]
        if missing:
            raise ScorerError(f"Columns not found: {missing}")


def _completeness(row: Dict[str, str], columns: Sequence[str]) -> float:
    """Fraction of specified columns that are non-empty."""
    if not columns:
        return 0.0
    filled = sum(1 for c in columns if row.get(c, "").strip() != "")
    return round(filled / len(columns), 4)


def _length_score(row: Dict[str, str], columns: Sequence[str]) -> float:
    """Mean normalised length (capped at 1.0 per cell, max_len=100)."""
    if not columns:
        return 0.0
    MAX_LEN = 100
    total = sum(min(len(row.get(c, "")), MAX_LEN) / MAX_LEN for c in columns)
    return round(total / len(columns), 4)


_METRICS = {
    "completeness": _completeness,
    "length": _length_score,
}


def score_rows(
    rows: List[Dict[str, str]],
    columns: Sequence[str],
    metric: str = "completeness",
    score_column: str = "_score",
) -> ScoreResult:
    if metric not in _METRICS:
        raise ScorerError(f"Unknown metric '{metric}'. Choose from: {list(_METRICS)}.")
    _validate(rows, columns)
    fn = _METRICS[metric]
    scored = [{**row, score_column: str(fn(row, columns))} for row in rows]
    return ScoreResult(rows=scored, score_column=score_column, metric=metric)
