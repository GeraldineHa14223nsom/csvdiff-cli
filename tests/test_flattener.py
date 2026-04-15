"""Tests for csvdiff.flattener."""
import pytest

from csvdiff.flattener import FlattenerError, flatten_column


ROWS = [
    {"id": "1", "name": "Alice", "meta": '{"age": 30, "city": "NY"}'},
    {"id": "2", "name": "Bob",   "meta": '{"age": 25, "city": "LA"}'},
    {"id": "3", "name": "Carol", "meta": '{"age": 40, "city": "SF"}'},
]


def test_flatten_creates_new_columns():
    result = flatten_column(ROWS, "meta")
    assert "age" in result.headers
    assert "city" in result.headers


def test_flatten_new_columns_listed():
    result = flatten_column(ROWS, "meta")
    assert set(result.new_columns) == {"age", "city"}


def test_flatten_values_extracted():
    result = flatten_column(ROWS, "meta")
    assert result.rows[0]["age"] == "30"
    assert result.rows[1]["city"] == "LA"


def test_flatten_source_column_preserved_by_default():
    result = flatten_column(ROWS, "meta")
    assert "meta" in result.headers


def test_flatten_drop_source_removes_column():
    result = flatten_column(ROWS, "meta", drop_source=True)
    assert "meta" not in result.headers
    for row in result.rows:
        assert "meta" not in row


def test_flatten_prefix_applied():
    result = flatten_column(ROWS, "meta", prefix="meta_")
    assert "meta_age" in result.headers
    assert "meta_city" in result.headers
    assert result.rows[0]["meta_age"] == "30"


def test_flatten_non_json_cell_gets_empty_strings():
    rows = [
        {"id": "1", "data": '{"x": 1}'},
        {"id": "2", "data": "not-json"},
    ]
    result = flatten_column(rows, "data")
    assert result.rows[1].get("x", "") == ""


def test_flatten_unknown_column_raises():
    with pytest.raises(FlattenerError, match="not found"):
        flatten_column(ROWS, "nonexistent")


def test_flatten_empty_rows_raises():
    with pytest.raises(FlattenerError, match="empty"):
        flatten_column([], "meta")


def test_flatten_source_column_field():
    result = flatten_column(ROWS, "meta")
    assert result.source_column == "meta"


def test_flatten_row_count_unchanged():
    result = flatten_column(ROWS, "meta")
    assert len(result.rows) == len(ROWS)


def test_flatten_original_columns_preserved():
    result = flatten_column(ROWS, "meta")
    assert "id" in result.headers
    assert "name" in result.headers
