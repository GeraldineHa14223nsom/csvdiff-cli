"""Column-level value comparison with configurable tolerance for numeric fields."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any


class ComparerError(Exception):
    def __str__(self) -> str:
        return f"ComparerError: {self.args[0]}"


@dataclass
class CompareResult:
    rows: List[Dict[str, Any]]
    mismatches: List[Dict[str, Any]]
    columns_compared: List[str]


def mismatch_count(result: CompareResult) -> int:
    return len(result.mismatches)


def match_rate(result: CompareResult) -> float:
    total = len(result.rows)
    if total == 0:
        return 1.0
    return (total - mismatch_count(result)) / total


def _validate(rows: List[Dict[str, Any]], columns: List[str]) -> None:
    if not columns:
        raise ComparerError("columns list must not be empty")
    if rows:
        missing = [c for c in columns if c not in rows[0]]
        if missing:
            raise ComparerError(f"columns not found in rows: {missing}")


def _values_equal(a: str, b: str, tolerance: float) -> bool:
    if a == b:
        return True
    if tolerance > 0:
        try:
            return abs(float(a) - float(b)) <= tolerance
        except (ValueError, TypeError):
            pass
    return False


def compare(
    left: List[Dict[str, Any]],
    right: List[Dict[str, Any]],
    columns: List[str],
    tolerance: float = 0.0,
) -> CompareResult:
    _validate(left, columns)
    _validate(right, columns)
    length = min(len(left), len(right))
    all_rows: List[Dict[str, Any]] = []
    mismatches: List[Dict[str, Any]] = []
    for i in range(length):
        l, r = left[i], right[i]
        row: Dict[str, Any] = {"_index": i}
        is_mismatch = False
        for col in columns:
            lv, rv = l.get(col, ""), r.get(col, "")
            eq = _values_equal(str(lv), str(rv), tolerance)
            row[f"{col}_left"] = lv
            row[f"{col}_right"] = rv
            row[f"{col}_match"] = eq
            if not eq:
                is_mismatch = True
        all_rows.append(row)
        if is_mismatch:
            mismatches.append(row)
    return CompareResult(rows=all_rows, mismatches=mismatches, columns_compared=columns)
