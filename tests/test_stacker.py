"""Unit tests for csvdiff.stacker."""
import pytest
from csvdiff.stacker import stack, StackResult, StackerError

DS1 = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
]
H1 = ["id", "name"]

DS2 = [
    {"id": "3", "name": "Carol"},
]
H2 = ["id", "name"]


def test_stack_total_rows():
    result = stack([DS1, DS2], [H1, H2])
    assert result.total_rows == 3


def test_stack_source_count():
    result = stack([DS1, DS2], [H1, H2])
    assert result.source_count == 2


def test_stack_source_counts_per_file():
    result = stack([DS1, DS2], [H1, H2])
    assert result.source_counts == [2, 1]


def test_stack_preserves_headers():
    result = stack([DS1, DS2], [H1, H2])
    assert result.headers == ["id", "name"]


def test_stack_row_values():
    result = stack([DS1, DS2], [H1, H2])
    assert result.rows[0] == {"id": "1", "name": "Alice"}
    assert result.rows[2] == {"id": "3", "name": "Carol"}


def test_stack_strict_raises_on_different_columns():
    ds3 = [{"id": "4", "email": "d@x.com"}]
    h3 = ["id", "email"]
    with pytest.raises(StackerError):
        stack([DS1, ds3], [H1, h3], strict=True)


def test_stack_no_strict_fills_missing():
    ds3 = [{"id": "4", "email": "d@x.com"}]
    h3 = ["id", "email"]
    result = stack([DS1, ds3], [H1, h3], strict=False, fill_value="N/A")
    assert "email" in result.headers
    assert "name" in result.headers
    # rows from DS1 should have fill for 'email'
    assert result.rows[0]["email"] == "N/A"
    # row from ds3 should have fill for 'name'
    assert result.rows[2]["name"] == "N/A"


def test_stack_no_datasets_raises():
    with pytest.raises(StackerError):
        stack([], [])


def test_stack_single_dataset():
    result = stack([DS1], [H1])
    assert result.total_rows == 2
    assert result.source_count == 1


def test_stack_empty_datasets():
    result = stack([[], []], [H1, H2])
    assert result.total_rows == 0
    assert result.source_counts == [0, 0]


def test_stack_result_is_stack_result_instance():
    result = stack([DS1, DS2], [H1, H2])
    assert isinstance(result, StackResult)
