"""Tests for csvdiff.reconcile."""
import pytest
from csvdiff.core import DiffResult
from csvdiff.reconcile import reconcile, reconcile_to_csv


KEY = ["id"]

BASE = [
    {"id": "1", "name": "Alice", "score": "10"},
    {"id": "2", "name": "Bob",   "score": "20"},
    {"id": "3", "name": "Carol", "score": "30"},
]


def _empty_diff() -> DiffResult:
    return DiffResult(added=[], removed=[], modified=[], unchanged=list(BASE))


def test_reconcile_no_changes():
    result = reconcile(_empty_diff(), BASE, KEY)
    assert result == BASE


def test_reconcile_added_rows():
    new_row = {"id": "4", "name": "Dave", "score": "40"}
    diff = DiffResult(added=[new_row], removed=[], modified=[], unchanged=list(BASE))
    result = reconcile(diff, BASE, KEY)
    assert new_row in result
    assert len(result) == len(BASE) + 1


def test_reconcile_removed_rows():
    diff = DiffResult(added=[], removed=[BASE[1]], modified=[], unchanged=[BASE[0], BASE[2]])
    result = reconcile(diff, BASE, KEY)
    assert all(r["id"] != "2" for r in result)
    assert len(result) == len(BASE) - 1


def test_reconcile_modified_rows():
    updated = {"id": "1", "name": "Alice", "score": "99"}
    diff = DiffResult(
        added=[],
        removed=[],
        modified=[{"old": BASE[0], "new": updated}],
        unchanged=[BASE[1], BASE[2]],
    )
    result = reconcile(diff, BASE, KEY)
    alice = next(r for r in result if r["id"] == "1")
    assert alice["score"] == "99"


def test_reconcile_to_csv_headers():
    csv_str = reconcile_to_csv(_empty_diff(), BASE, KEY)
    first_line = csv_str.splitlines()[0]
    assert "id" in first_line and "name" in first_line and "score" in first_line


def test_reconcile_to_csv_row_count():
    new_row = {"id": "5", "name": "Eve", "score": "50"}
    diff = DiffResult(added=[new_row], removed=[], modified=[], unchanged=list(BASE))
    csv_str = reconcile_to_csv(diff, BASE, KEY)
    # header + 4 data rows
    assert len(csv_str.splitlines()) == 5


def test_reconcile_to_csv_empty_result():
    diff = DiffResult(added=[], removed=list(BASE), modified=[], unchanged=[])
    csv_str = reconcile_to_csv(diff, BASE, KEY)
    assert csv_str == ""
