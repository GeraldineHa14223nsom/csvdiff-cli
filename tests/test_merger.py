"""Tests for csvdiff.merger."""
import pytest

from csvdiff.core import DiffResult
from csvdiff.merger import MergeError, MergeResult, merge

HEADERS = ["id", "name", "score"]
KEYS = ["id"]


@pytest.fixture()
def base_rows():
    return [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob", "score": "80"},
        {"id": "3", "name": "Carol", "score": "70"},
    ]


@pytest.fixture()
def empty_diff():
    return DiffResult(added=[], removed=[], modified=[], unchanged=[])


def test_merge_no_changes_returns_base(base_rows, empty_diff):
    result = merge(empty_diff, KEYS, base=base_rows)
    assert result.rows == base_rows
    assert not result.has_conflicts


def test_merge_added_row_appears(base_rows, empty_diff):
    new_row = {"id": "4", "name": "Dave", "score": "60"}
    diff = DiffResult(added=[new_row], removed=[], modified=[], unchanged=[])
    result = merge(diff, KEYS, base=base_rows)
    assert new_row in result.rows
    assert len(result.rows) == 4


def test_merge_removed_row_absent(base_rows, empty_diff):
    removed = {"id": "2", "name": "Bob", "score": "80"}
    diff = DiffResult(added=[], removed=[removed], modified=[], unchanged=[])
    result = merge(diff, KEYS, base=base_rows)
    ids = [r["id"] for r in result.rows]
    assert "2" not in ids
    assert len(result.rows) == 2


def test_merge_strategy_ours_keeps_old(base_rows):
    old = {"id": "1", "name": "Alice", "score": "90"}
    new = {"id": "1", "name": "Alice", "score": "95"}
    diff = DiffResult(added=[], removed=[], modified=[(old, new)], unchanged=[])
    result = merge(diff, KEYS, strategy="ours", base=base_rows)
    merged = next(r for r in result.rows if r["id"] == "1")
    assert merged["score"] == "90"
    assert result.has_conflicts


def test_merge_strategy_theirs_keeps_new(base_rows):
    old = {"id": "1", "name": "Alice", "score": "90"}
    new = {"id": "1", "name": "Alice", "score": "95"}
    diff = DiffResult(added=[], removed=[], modified=[(old, new)], unchanged=[])
    result = merge(diff, KEYS, strategy="theirs", base=base_rows)
    merged = next(r for r in result.rows if r["id"] == "1")
    assert merged["score"] == "95"
    assert result.has_conflicts


def test_merge_strategy_raise_on_conflict(base_rows):
    old = {"id": "1", "name": "Alice", "score": "90"}
    new = {"id": "1", "name": "Alice", "score": "95"}
    diff = DiffResult(added=[], removed=[], modified=[(old, new)], unchanged=[])
    with pytest.raises(MergeError, match="Conflict on key"):
        merge(diff, KEYS, strategy="raise", base=base_rows)


def test_merge_unknown_strategy_raises(base_rows, empty_diff):
    with pytest.raises(MergeError, match="Unknown merge strategy"):
        merge(empty_diff, KEYS, strategy="magic", base=base_rows)


def test_merge_no_base_uses_added_only():
    row = {"id": "1", "name": "Alice", "score": "90"}
    diff = DiffResult(added=[row], removed=[], modified=[], unchanged=[])
    result = merge(diff, KEYS)
    assert result.rows == [row]
    assert not result.has_conflicts


def test_merge_multiple_conflicts_all_recorded(base_rows):
    """All conflicting rows should be tracked when strategy is not 'raise'."""
    old1 = {"id": "1", "name": "Alice", "score": "90"}
    new1 = {"id": "1", "name": "Alice", "score": "95"}
    old2 = {"id": "2", "name": "Bob", "score": "80"}
    new2 = {"id": "2", "name": "Bob", "score": "85"}
    diff = DiffResult(
        added=[],
        removed=[],
        modified=[(old1, new1), (old2, new2)],
        unchanged=[],
    )
    result = merge(diff, KEYS, strategy="ours", base=base_rows)
    assert result.has_conflicts
    assert len(result.conflicts) == 2
