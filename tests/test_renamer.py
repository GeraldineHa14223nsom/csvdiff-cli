"""Tests for csvdiff.renamer."""
import pytest

from csvdiff.renamer import (
    RenameResult,
    RenamerError,
    iter_renamed,
    rename_columns,
)


ROWS = [
    {"id": "1", "first_name": "Alice", "score": "90"},
    {"id": "2", "first_name": "Bob", "score": "85"},
]


def test_rename_single_column():
    result = rename_columns(ROWS, {"first_name": "name"})
    assert all("name" in r for r in result.rows)
    assert all("first_name" not in r for r in result.rows)


def test_rename_preserves_other_columns():
    result = rename_columns(ROWS, {"first_name": "name"})
    assert result.rows[0]["id"] == "1"
    assert result.rows[0]["score"] == "90"


def test_rename_multiple_columns():
    result = rename_columns(ROWS, {"first_name": "name", "score": "points"})
    assert result.rows[0]["name"] == "Alice"
    assert result.rows[0]["points"] == "90"


def test_rename_preserves_values():
    result = rename_columns(ROWS, {"first_name": "name"})
    assert result.rows[1]["name"] == "Bob"


def test_rename_empty_mapping_passthrough():
    result = rename_columns(ROWS, {})
    assert result.rows == ROWS


def test_rename_empty_rows_returns_empty_result():
    result = rename_columns([], {"first_name": "name"})
    assert result.rows == []
    assert isinstance(result, RenameResult)


def test_rename_unknown_column_raises():
    with pytest.raises(RenamerError) as exc_info:
        rename_columns(ROWS, {"nonexistent": "new_name"})
    assert "nonexistent" in str(exc_info.value)


def test_rename_multiple_unknown_columns_raises():
    with pytest.raises(RenamerError) as exc_info:
        rename_columns(ROWS, {"bad1": "x", "bad2": "y"})
    assert "bad1" in str(exc_info.value) or "bad2" in str(exc_info.value)


def test_rename_result_stores_mapping():
    mapping = {"first_name": "name"}
    result = rename_columns(ROWS, mapping)
    assert result.mapping == mapping


def test_iter_renamed_yields_correct_rows():
    renamed = list(iter_renamed(ROWS, {"first_name": "name"}))
    assert len(renamed) == 2
    assert renamed[0]["name"] == "Alice"
    assert "first_name" not in renamed[0]


def test_iter_renamed_empty_input():
    renamed = list(iter_renamed([], {"first_name": "name"}))
    assert renamed == []
