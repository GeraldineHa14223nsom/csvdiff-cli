"""Tests for csvdiff.shrinker."""
import pytest
from csvdiff.shrinker import shrink, ShrinkResult, ShrinkerError


@pytest.fixture
def rows():
    return [
        {"id": "1", "name": "Alice",                   "note": "short"},
        {"id": "2", "name": "Bob",                     "note": "a very long note that exceeds the limit"},
        {"id": "3", "name": "Christopher Columbus",   "note": "medium note here"},
        {"id": "4", "name": "Di",                      "note": ""},
    ]


def test_returns_shrink_result(rows):
    result = shrink(rows, column="note", max_length=10)
    assert isinstance(result, ShrinkResult)


def test_row_count_unchanged(rows):
    result = shrink(rows, column="note", max_length=10)
    assert result.row_count == len(rows)


def test_short_values_not_truncated(rows):
    result = shrink(rows, column="note", max_length=10)
    assert result.rows[0]["note"] == "short"


def test_long_value_truncated(rows):
    result = shrink(rows, column="note", max_length=10)
    val = result.rows[1]["note"]
    assert len(val) == 10
    assert val.endswith("...")


def test_truncated_count(rows):
    result = shrink(rows, column="note", max_length=10)
    # rows 1 and 2 exceed 10 chars
    assert result.truncated_count == 2


def test_truncation_rate(rows):
    result = shrink(rows, column="note", max_length=10)
    assert abs(result.truncation_rate - 0.5) < 1e-9


def test_empty_value_not_truncated(rows):
    result = shrink(rows, column="note", max_length=10)
    assert result.rows[3]["note"] == ""


def test_other_columns_preserved(rows):
    result = shrink(rows, column="note", max_length=10)
    assert result.rows[0]["id"] == "1"
    assert result.rows[0]["name"] == "Alice"


def test_custom_ellipsis(rows):
    result = shrink(rows, column="note", max_length=12, ellipsis_str="--")
    val = result.rows[1]["note"]
    assert len(val) == 12
    assert val.endswith("--")


def test_max_length_shorter_than_ellipsis(rows):
    # max_length <= len(ellipsis) → just slice the ellipsis
    result = shrink(rows, column="note", max_length=2)
    val = result.rows[1]["note"]
    assert len(val) <= 2


def test_unknown_column_raises(rows):
    with pytest.raises(ShrinkerError):
        shrink(rows, column="nonexistent", max_length=10)


def test_invalid_max_length_raises(rows):
    with pytest.raises(ShrinkerError):
        shrink(rows, column="note", max_length=0)


def test_empty_rows_returns_result():
    result = shrink([], column="note", max_length=10)
    assert result.row_count == 0
    assert result.truncated_count == 0


def test_headers_stored(rows):
    result = shrink(rows, column="note", max_length=10)
    assert result.headers == ["id", "name", "note"]


def test_column_and_max_length_stored(rows):
    result = shrink(rows, column="name", max_length=5)
    assert result.column == "name"
    assert result.max_length == 5
