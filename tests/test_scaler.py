"""Tests for csvdiff.scaler."""
import pytest
from csvdiff.scaler import scale, ScaleResult, ScalerError


@pytest.fixture
def rows():
    return [
        {"id": "1", "score": "10"},
        {"id": "2", "score": "20"},
        {"id": "3", "score": "30"},
        {"id": "4", "score": "40"},
        {"id": "5", "score": "50"},
    ]


def test_returns_scale_result(rows):
    result = scale(rows, "score")
    assert isinstance(result, ScaleResult)


def test_scaled_count(rows):
    result = scale(rows, "score")
    assert result.scaled_count == 5


def test_row_count(rows):
    result = scale(rows, "score")
    assert result.row_count == 5


def test_minmax_min_is_zero(rows):
    result = scale(rows, "score", method="minmax")
    values = [float(r["score"]) for r in result.rows]
    assert values[0] == pytest.approx(0.0)


def test_minmax_max_is_one(rows):
    result = scale(rows, "score", method="minmax")
    values = [float(r["score"]) for r in result.rows]
    assert values[-1] == pytest.approx(1.0)


def test_minmax_midpoint(rows):
    result = scale(rows, "score", method="minmax")
    values = [float(r["score"]) for r in result.rows]
    assert values[2] == pytest.approx(0.5)


def test_zscore_mean_near_zero(rows):
    result = scale(rows, "score", method="zscore")
    values = [float(r["score"]) for r in result.rows]
    assert sum(values) / len(values) == pytest.approx(0.0, abs=1e-9)


def test_zscore_preserves_other_columns(rows):
    result = scale(rows, "score", method="zscore")
    ids = [r["id"] for r in result.rows]
    assert ids == ["1", "2", "3", "4", "5"]


def test_original_min_max_stored(rows):
    result = scale(rows, "score")
    assert result.original_min == pytest.approx(10.0)
    assert result.original_max == pytest.approx(50.0)


def test_method_stored(rows):
    result = scale(rows, "score", method="zscore")
    assert result.method == "zscore"


def test_column_stored(rows):
    result = scale(rows, "score")
    assert result.column == "score"


def test_unknown_method_raises(rows):
    with pytest.raises(ScalerError, match="unknown method"):
        scale(rows, "score", method="log")


def test_missing_column_raises(rows):
    with pytest.raises(ScalerError, match="not found"):
        scale(rows, "missing")


def test_non_numeric_raises(rows):
    bad = [{"score": "abc"}]
    with pytest.raises(ScalerError, match="non-numeric"):
        scale(bad, "score")


def test_empty_rows_raises():
    with pytest.raises(ScalerError, match="empty"):
        scale([], "score")


def test_constant_column_minmax():
    rows = [{"v": "5"}, {"v": "5"}, {"v": "5"}]
    result = scale(rows, "v", method="minmax")
    values = [float(r["v"]) for r in result.rows]
    assert all(v == pytest.approx(0.0) for v in values)


def test_constant_column_zscore():
    rows = [{"v": "7"}, {"v": "7"}, {"v": "7"}]
    result = scale(rows, "v", method="zscore")
    values = [float(r["v"]) for r in result.rows]
    assert all(v == pytest.approx(0.0) for v in values)
