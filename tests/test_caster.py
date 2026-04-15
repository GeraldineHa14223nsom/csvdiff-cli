"""Tests for csvdiff.caster."""

import pytest

from csvdiff.caster import (
    CasterError,
    CastResult,
    cast_columns,
)


HEADERS = ["id", "name", "score", "active"]


def _rows():
    return [
        {"id": "1", "name": "Alice", "score": "9.5", "active": "true"},
        {"id": "2", "name": "Bob", "score": "7.0", "active": "false"},
        {"id": "3", "name": "Carol", "score": "8.25", "active": "1"},
    ]


def test_cast_int_column():
    result = cast_columns(HEADERS, _rows(), {"id": "int"})
    assert isinstance(result, CastResult)
    assert result.rows[0]["id"] == "1"
    assert result.cast_count == 3
    assert result.error_count == 0


def test_cast_float_column():
    result = cast_columns(HEADERS, _rows(), {"score": "float"})
    assert result.rows[1]["score"] == "7.0"
    assert result.cast_count == 3


def test_cast_bool_true_variants():
    result = cast_columns(HEADERS, _rows(), {"active": "bool"})
    assert result.rows[0]["active"] == "True"
    assert result.rows[1]["active"] == "False"
    assert result.rows[2]["active"] == "True"


def test_cast_str_is_noop():
    result = cast_columns(HEADERS, _rows(), {"name": "str"})
    assert result.rows[0]["name"] == "Alice"
    assert result.cast_count == 3


def test_cast_multiple_columns():
    result = cast_columns(HEADERS, _rows(), {"id": "int", "score": "float"})
    assert result.cast_count == 6  # 3 rows x 2 columns


def test_unknown_type_raises():
    with pytest.raises(CasterError, match="Unsupported type"):
        cast_columns(HEADERS, _rows(), {"id": "datetime"})


def test_unknown_column_raises():
    with pytest.raises(CasterError, match="not found in headers"):
        cast_columns(HEADERS, _rows(), {"missing": "int"})


def test_bad_int_value_non_strict_records_error():
    rows = [{"id": "abc", "name": "X", "score": "1.0", "active": "true"}]
    result = cast_columns(HEADERS, rows, {"id": "int"}, strict=False)
    assert result.error_count == 1
    assert result.rows[0]["id"] == "abc"  # original preserved
    assert len(result.errors) == 1


def test_bad_int_value_strict_raises():
    rows = [{"id": "abc", "name": "X", "score": "1.0", "active": "true"}]
    with pytest.raises(CasterError):
        cast_columns(HEADERS, rows, {"id": "int"}, strict=True)


def test_bad_bool_value_non_strict():
    rows = [{"id": "1", "name": "X", "score": "1.0", "active": "maybe"}]
    result = cast_columns(HEADERS, rows, {"active": "bool"}, strict=False)
    assert result.error_count == 1
    assert result.rows[0]["active"] == "maybe"


def test_empty_rows_returns_empty_result():
    result = cast_columns(HEADERS, [], {"id": "int"})
    assert result.rows == []
    assert result.cast_count == 0
    assert result.error_count == 0


def test_headers_preserved_in_result():
    result = cast_columns(HEADERS, _rows(), {"id": "int"})
    assert result.headers == HEADERS
