"""Tests for csvdiff.truncator."""

import pytest
from csvdiff.truncator import truncate, TruncateResult, TruncatorError


ROWS = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "3", "name": "Carol"},
    {"id": "4", "name": "Dave"},
    {"id": "5", "name": "Eve"},
]


def test_head_returns_first_n_rows():
    result = truncate(ROWS, 3, mode="head")
    assert [r["id"] for r in result.rows] == ["1", "2", "3"]


def test_tail_returns_last_n_rows():
    result = truncate(ROWS, 2, mode="tail")
    assert [r["id"] for r in result.rows] == ["4", "5"]


def test_default_mode_is_head():
    result = truncate(ROWS, 2)
    assert [r["id"] for r in result.rows] == ["1", "2"]


def test_original_count_preserved():
    result = truncate(ROWS, 3)
    assert result.original_count == 5


def test_truncated_count_correct():
    result = truncate(ROWS, 3)
    assert result.truncated_count == 3


def test_removed_count_property():
    result = truncate(ROWS, 3)
    assert result.removed_count == 2


def test_n_larger_than_rows_returns_all():
    result = truncate(ROWS, 100)
    assert result.truncated_count == 5
    assert result.removed_count == 0


def test_n_zero_head_returns_empty():
    result = truncate(ROWS, 0, mode="head")
    assert result.rows == []
    assert result.truncated_count == 0


def test_n_zero_tail_returns_empty():
    result = truncate(ROWS, 0, mode="tail")
    assert result.rows == []


def test_empty_rows_returns_empty_result():
    result = truncate([], 3)
    assert result.rows == []
    assert result.original_count == 0


def test_negative_n_raises():
    with pytest.raises(TruncatorError, match="non-negative"):
        truncate(ROWS, -1)


def test_invalid_mode_raises():
    with pytest.raises(TruncatorError, match="mode"):
        truncate(ROWS, 3, mode="middle")


def test_truncator_error_str():
    err = TruncatorError("bad input")
    assert "TruncatorError" in str(err)
    assert "bad input" in str(err)


def test_result_is_dataclass_instance():
    result = truncate(ROWS, 2)
    assert isinstance(result, TruncateResult)
