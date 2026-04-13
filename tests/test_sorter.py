"""Tests for csvdiff.sorter."""

import pytest
from csvdiff.core import DiffResult
from csvdiff.sorter import SortError, sort_rows, sort_result


ROWS = [
    {"id": "3", "name": "Charlie"},
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
]


def test_sort_rows_asc():
    result = sort_rows(ROWS, "id")
    assert [r["id"] for r in result] == ["1", "2", "3"]


def test_sort_rows_desc():
    result = sort_rows(ROWS, "id", direction="desc")
    assert [r["id"] for r in result] == ["3", "2", "1"]


def test_sort_rows_by_name():
    result = sort_rows(ROWS, "name")
    assert [r["name"] for r in result] == ["Alice", "Bob", "Charlie"]


def test_sort_rows_empty():
    assert sort_rows([], "id") == []


def test_sort_rows_unknown_column_raises():
    with pytest.raises(SortError, match="nope"):
        sort_rows(ROWS, "nope")


def test_sort_rows_invalid_direction_raises():
    with pytest.raises(SortError, match="direction"):
        sort_rows(ROWS, "id", direction="random")


def test_sort_rows_with_explicit_available():
    result = sort_rows(ROWS, "id", available=["id", "name"])
    assert [r["id"] for r in result] == ["1", "2", "3"]


def test_sort_rows_explicit_available_unknown_raises():
    with pytest.raises(SortError):
        sort_rows(ROWS, "missing", available=["id", "name"])


@pytest.fixture()
def diff_result():
    return DiffResult(
        added=[{"id": "3", "v": "c"}, {"id": "1", "v": "a"}],
        removed=[{"id": "2", "v": "b"}],
        modified=[
            {"before": {"id": "5", "v": "x"}, "after": {"id": "5", "v": "y"}},
            {"before": {"id": "4", "v": "w"}, "after": {"id": "4", "v": "z"}},
        ],
        unchanged=[{"id": "9", "v": "q"}, {"id": "6", "v": "p"}],
    )


def test_sort_result_added(diff_result):
    sorted_r = sort_result(diff_result, "id")
    assert [r["id"] for r in sorted_r.added] == ["1", "3"]


def test_sort_result_removed(diff_result):
    sorted_r = sort_result(diff_result, "id")
    assert [r["id"] for r in sorted_r.removed] == ["2"]


def test_sort_result_modified(diff_result):
    sorted_r = sort_result(diff_result, "id")
    assert [r["before"]["id"] for r in sorted_r.modified] == ["4", "5"]


def test_sort_result_unchanged(diff_result):
    sorted_r = sort_result(diff_result, "id")
    assert [r["id"] for r in sorted_r.unchanged] == ["6", "9"]


def test_sort_result_desc(diff_result):
    sorted_r = sort_result(diff_result, "id", direction="desc")
    assert [r["id"] for r in sorted_r.added] == ["3", "1"]


def test_sort_result_empty_diff():
    empty = DiffResult(added=[], removed=[], modified=[], unchanged=[])
    sorted_r = sort_result(empty, "id")
    assert sorted_r.added == []
