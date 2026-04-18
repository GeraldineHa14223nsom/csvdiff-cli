"""Tests for csvdiff.scorer."""
import pytest
from csvdiff.scorer import score_rows, ScoreResult, ScorerError


@pytest.fixture
def rows():
    return [
        {"id": "1", "name": "Alice", "city": "London"},
        {"id": "2", "name": "", "city": "Paris"},
        {"id": "3", "name": "", "city": ""},
    ]


def test_returns_score_result(rows):
    result = score_rows(rows, ["name", "city"])
    assert isinstance(result, ScoreResult)


def test_scored_count(rows):
    result = score_rows(rows, ["name", "city"])
    assert result.scored_count() == 3


def test_completeness_all_filled(rows):
    result = score_rows(rows, ["name", "city"])
    assert result.rows[0]["_score"] == "1.0"


def test_completeness_half_filled(rows):
    result = score_rows(rows, ["name", "city"])
    assert result.rows[1]["_score"] == "0.5"


def test_completeness_none_filled(rows):
    result = score_rows(rows, ["name", "city"])
    assert result.rows[2]["_score"] == "0.0"


def test_mean_score(rows):
    result = score_rows(rows, ["name", "city"])
    expected = round((1.0 + 0.5 + 0.0) / 3, 4)
    assert abs(result.mean_score() - expected) < 1e-6


def test_custom_score_column(rows):
    result = score_rows(rows, ["name"], score_column="quality")
    assert "quality" in result.rows[0]
    assert result.score_column == "quality"


def test_length_metric(rows):
    result = score_rows(rows, ["name", "city"], metric="length")
    assert result.metric == "length"
    score = float(result.rows[0]["_score"])
    assert 0.0 < score <= 1.0


def test_unknown_metric_raises(rows):
    with pytest.raises(ScorerError, match="Unknown metric"):
        score_rows(rows, ["name"], metric="bogus")


def test_empty_columns_raises(rows):
    with pytest.raises(ScorerError, match="At least one column"):
        score_rows(rows, [])


def test_missing_column_raises(rows):
    with pytest.raises(ScorerError, match="Columns not found"):
        score_rows(rows, ["nonexistent"])


def test_empty_rows_returns_zero_mean():
    result = score_rows([], ["name"], metric="completeness")
    assert result.mean_score() == 0.0
    assert result.scored_count() == 0
