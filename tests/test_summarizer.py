"""Tests for csvdiff.summarizer."""
import pytest
from csvdiff.summarizer import summarize, SummarizerError, SummaryResult


@pytest.fixture
def rows():
    return [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob",   "score": "80"},
        {"id": "3", "name": "",      "score": "70"},
        {"id": "4", "name": "Dana",  "score": "not_a_number"},
    ]


def test_returns_summary_result(rows):
    result = summarize(rows)
    assert isinstance(result, SummaryResult)


def test_row_count(rows):
    result = summarize(rows)
    assert result.row_count == 4


def test_column_count(rows):
    result = summarize(rows)
    assert len(result.columns) == 3


def test_fill_rate_full_column(rows):
    result = summarize(rows)
    col = result.get("id")
    assert col is not None
    assert col.fill_rate == 1.0


def test_fill_rate_partial_column(rows):
    result = summarize(rows)
    col = result.get("name")
    assert col.non_empty == 3
    assert col.empty_count == 1
    assert col.fill_rate == pytest.approx(0.75)


def test_numeric_count(rows):
    result = summarize(rows)
    col = result.get("score")
    assert col.numeric_count == 3


def test_min_value(rows):
    result = summarize(rows)
    col = result.get("score")
    assert col.min_value == pytest.approx(70.0)


def test_max_value(rows):
    result = summarize(rows)
    col = result.get("score")
    assert col.max_value == pytest.approx(90.0)


def test_mean_value(rows):
    result = summarize(rows)
    col = result.get("score")
    assert col.mean_value == pytest.approx(80.0)


def test_non_numeric_column_has_no_stats(rows):
    result = summarize(rows)
    col = result.get("name")
    assert col.min_value is None
    assert col.max_value is None
    assert col.mean_value is None


def test_subset_columns(rows):
    result = summarize(rows, columns=["score"])
    assert len(result.columns) == 1
    assert result.columns[0].column == "score"


def test_unknown_column_raises(rows):
    with pytest.raises(SummarizerError):
        summarize(rows, columns=["nonexistent"])


def test_empty_rows_returns_empty_result():
    result = summarize([])
    assert result.row_count == 0
    assert result.columns == []


def test_get_returns_none_for_missing_column(rows):
    result = summarize(rows)
    assert result.get("missing") is None
