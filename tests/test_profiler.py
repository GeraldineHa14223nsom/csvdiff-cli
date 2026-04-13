"""Tests for csvdiff.profiler."""
import pytest
from csvdiff.profiler import profile_rows, ProfileResult, ColumnProfile


ROWS = [
    {"id": "1", "name": "Alice", "score": "95"},
    {"id": "2", "name": "Bob",   "score": ""},
    {"id": "3", "name": "Alice", "score": "88"},
]


def test_profile_returns_all_columns():
    result = profile_rows(ROWS)
    assert result.columns == ["id", "name", "score"]


def test_profile_count():
    result = profile_rows(ROWS)
    assert result.profiles["id"].count == 3


def test_profile_non_empty():
    result = profile_rows(ROWS)
    assert result.profiles["score"].non_empty == 2


def test_profile_empty_count():
    result = profile_rows(ROWS)
    assert result.profiles["score"].empty_count == 1


def test_profile_fill_rate():
    result = profile_rows(ROWS)
    assert result.profiles["score"].fill_rate == pytest.approx(2 / 3)


def test_profile_unique_values():
    result = profile_rows(ROWS)
    # "Alice" appears twice, "Bob" once
    assert result.profiles["name"].unique_values == 2


def test_profile_min_max_length():
    result = profile_rows(ROWS)
    p = result.profiles["name"]
    assert p.min_length == 3  # "Bob"
    assert p.max_length == 5  # "Alice"


def test_profile_sample_values_capped():
    rows = [{"x": str(i)} for i in range(20)]
    result = profile_rows(rows, sample_size=3)
    assert len(result.profiles["x"].sample_values) == 3


def test_profile_empty_rows_returns_empty_result():
    result = profile_rows([])
    assert result.columns == []
    assert result.profiles == {}


def test_profile_all_empty_values():
    rows = [{"col": ""}, {"col": ""}, {"col": ""}]
    result = profile_rows(rows)
    assert result.profiles["col"].fill_rate == 0.0
    assert result.profiles["col"].empty_count == 3
