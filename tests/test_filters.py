"""Tests for csvdiff.filters."""
import pytest

from csvdiff.filters import exclude_rows, filter_columns, filter_rows

ROWS = [
    {"id": "1", "name": "Alice", "dept": "eng"},
    {"id": "2", "name": "Bob", "dept": "hr"},
    {"id": "3", "name": "Carol", "dept": "eng"},
]


def test_filter_columns_include():
    result = filter_columns(ROWS, include=["id", "name"])
    assert result == [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}, {"id": "3", "name": "Carol"}]


def test_filter_columns_exclude():
    result = filter_columns(ROWS, exclude=["dept"])
    assert all("dept" not in r for r in result)
    assert all("id" in r for r in result)


def test_filter_columns_include_takes_precedence():
    result = filter_columns(ROWS, include=["id"], exclude=["name"])
    assert result == [{"id": "1"2"}, {"id": "3"}]


def test_filter_columns_unknown_raises():
    with pytest. columns"):
        filter_columns(ROWS, include=["id", "missing"])


def test_filter_columns_empty():
    assert filter_columns([], include=["id"]) == []


def test_filter_columns_no_filters():
    result = filter_columns(ROWS)
    assert result == ROWS


def test_filter_rows_keep():
    result = filter_rows(ROWS, "dept", ["eng"])
    assert len(result) == 2
    assert all(r["dept"] == "eng" for r in result)


def test_filter_rows_no_match():
    result = filter_rows(ROWS, "dept", ["finance"])
    assert result == []


def test_exclude_rows():
    result = exclude_rows(ROWS, "dept", ["hr"])
    assert len(result) == 2
    assert all(r["dept"] != "hr" for r in result)


def test_exclude_rows_empty_exclusion():
    result = exclude_rows(ROWS, "dept", [])
    assert result == ROWS
