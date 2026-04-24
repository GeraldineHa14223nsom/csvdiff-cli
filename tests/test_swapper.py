"""Tests for csvdiff.swapper."""
import pytest
from csvdiff.swapper import swap_columns, SwapperError, SwapResult


@pytest.fixture()
def rows():
    return [
        {"id": "1", "first": "Alice", "last": "Smith"},
        {"id": "2", "first": "Bob",   "last": "Jones"},
        {"id": "3", "first": "Carol", "last": "Carol"},  # same value in both
    ]


def test_returns_swap_result(rows):
    result = swap_columns(rows, "first", "last")
    assert isinstance(result, SwapResult)


def test_row_count_unchanged(rows):
    result = swap_columns(rows, "first", "last")
    assert result.row_count == len(rows)


def test_values_exchanged(rows):
    result = swap_columns(rows, "first", "last")
    assert result.rows[0]["first"] == "Smith"
    assert result.rows[0]["last"] == "Alice"


def test_second_row_exchanged(rows):
    result = swap_columns(rows, "first", "last")
    assert result.rows[1]["first"] == "Jones"
    assert result.rows[1]["last"] == "Bob"


def test_unrelated_columns_untouched(rows):
    result = swap_columns(rows, "first", "last")
    assert result.rows[0]["id"] == "1"
    assert result.rows[1]["id"] == "2"


def test_original_rows_not_mutated(rows):
    original_first = rows[0]["first"]
    swap_columns(rows, "first", "last")
    assert rows[0]["first"] == original_first


def test_swapped_count_excludes_identical_values(rows):
    result = swap_columns(rows, "first", "last")
    # Row 3 has first == last == "Carol", so only 2 rows truly differ
    assert result.swapped_count == 2


def test_swapped_count_all_different():
    data = [
        {"a": "x", "b": "y"},
        {"a": "p", "b": "q"},
    ]
    result = swap_columns(data, "a", "b")
    assert result.swapped_count == 2


def test_empty_rows_returns_empty_result():
    result = swap_columns([], "a", "b")
    assert result.row_count == 0
    assert result.rows == []


def test_missing_col_a_raises(rows):
    with pytest.raises(SwapperError, match="not found"):
        swap_columns(rows, "missing", "last")


def test_missing_col_b_raises(rows):
    with pytest.raises(SwapperError, match="not found"):
        swap_columns(rows, "first", "missing")


def test_same_column_raises(rows):
    with pytest.raises(SwapperError, match="different"):
        swap_columns(rows, "first", "first")


def test_col_a_and_col_b_stored_on_result(rows):
    result = swap_columns(rows, "first", "last")
    assert result.col_a == "first"
    assert result.col_b == "last"
