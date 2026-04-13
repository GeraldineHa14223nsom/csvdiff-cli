"""Tests for csvdiff.aggregator."""
import pytest

from csvdiff.aggregator import (
    AggregateResult,
    AggregatorError,
    aggregate_all,
    aggregate_column,
)

ROWS = [
    {"name": "Alice", "score": "10", "age": "30"},
    {"name": "Bob", "score": "20", "age": "25"},
    {"name": "Carol", "score": "30", "age": "35"},
]


def test_aggregate_count():
    result = aggregate_column(ROWS, "score")
    assert result.count == 3


def test_aggregate_total():
    result = aggregate_column(ROWS, "score")
    assert result.total == pytest.approx(60.0)


def test_aggregate_minimum():
    result = aggregate_column(ROWS, "score")
    assert result.minimum == pytest.approx(10.0)


def test_aggregate_maximum():
    result = aggregate_column(ROWS, "score")
    assert result.maximum == pytest.approx(30.0)


def test_aggregate_mean():
    result = aggregate_column(ROWS, "score")
    assert result.mean == pytest.approx(20.0)


def test_aggregate_column_field():
    result = aggregate_column(ROWS, "age")
    assert result.column == "age"


def test_aggregate_non_numeric_returns_none_stats():
    result = aggregate_column(ROWS, "name")
    assert result.count == 0
    assert result.minimum is None
    assert result.maximum is None
    assert result.mean is None


def test_aggregate_unknown_column_raises():
    with pytest.raises(AggregatorError, match="not found"):
        aggregate_column(ROWS, "missing")


def test_aggregate_empty_rows_raises():
    with pytest.raises(AggregatorError, match="No rows"):
        aggregate_column([], "score")


def test_aggregate_all_returns_dict():
    results = aggregate_all(ROWS, ["score", "age"])
    assert set(results.keys()) == {"score", "age"}
    assert isinstance(results["score"], AggregateResult)


def test_aggregate_all_values():
    results = aggregate_all(ROWS, ["score"])
    assert results["score"].total == pytest.approx(60.0)


def test_aggregate_mixed_numeric_and_blank():
    rows = [
        {"val": "5"},
        {"val": ""},
        {"val": "15"},
    ]
    result = aggregate_column(rows, "val")
    assert result.count == 2
    assert result.total == pytest.approx(20.0)
    assert result.mean == pytest.approx(10.0)
