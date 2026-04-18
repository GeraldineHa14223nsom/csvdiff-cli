import math
import pytest
from csvdiff.correlator import correlate, CorrelatorError


@pytest.fixture
def rows():
    return [
        {"id": "1", "x": "1", "y": "2", "z": "5"},
        {"id": "2", "x": "2", "y": "4", "z": "4"},
        {"id": "3", "x": "3", "y": "6", "z": "3"},
        {"id": "4", "x": "4", "y": "8", "z": "2"},
    ]


def test_perfect_positive_correlation(rows):
    result = correlate(rows, ["x", "y"])
    assert result.matrix["x"]["y"] == pytest.approx(1.0, abs=1e-5)


def test_perfect_negative_correlation(rows):
    result = correlate(rows, ["x", "z"])
    assert result.matrix["x"]["z"] == pytest.approx(-1.0, abs=1e-5)


def test_self_correlation_is_one(rows):
    result = correlate(rows, ["x", "y"])
    assert result.matrix["x"]["x"] == pytest.approx(1.0)


def test_matrix_is_symmetric(rows):
    result = correlate(rows, ["x", "y", "z"])
    assert result.matrix["x"]["y"] == result.matrix["y"]["x"]
    assert result.matrix["x"]["z"] == result.matrix["z"]["x"]


def test_result_columns(rows):
    result = correlate(rows, ["x", "z"])
    assert result.columns == ["x", "z"]


def test_unknown_column_raises(rows):
    with pytest.raises(CorrelatorError, match="Column not found"):
        correlate(rows, ["x", "missing"])


def test_single_column_raises(rows):
    with pytest.raises(CorrelatorError, match="At least two"):
        correlate(rows, ["x"])


def test_empty_rows_raises():
    with pytest.raises(CorrelatorError, match="No rows"):
        correlate([], ["x", "y"])


def test_non_numeric_raises(rows):
    bad = [{"x": "a", "y": "1"} for _ in rows]
    with pytest.raises(CorrelatorError, match="Non-numeric"):
        correlate(bad, ["x", "y"])


def test_constant_column_returns_nan(rows):
    flat = [{"x": str(i), "y": "5"} for i in range(1, 5)]
    result = correlate(flat, ["x", "y"])
    assert math.isnan(result.matrix["x"]["y"])
