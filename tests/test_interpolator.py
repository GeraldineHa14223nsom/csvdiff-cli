"""Tests for csvdiff.interpolator."""
import pytest
from csvdiff.interpolator import interpolate, InterpolateResult, InterpolatorError


def _rows(*score_values):
    return [{"id": str(i + 1), "score": v} for i, v in enumerate(score_values)]


# ---------------------------------------------------------------------------
# basic happy-path
# ---------------------------------------------------------------------------

def test_returns_interpolate_result():
    rows = _rows("1.0", "", "3.0")
    result = interpolate(rows, ["score"])
    assert isinstance(result, InterpolateResult)


def test_filled_count_single_gap():
    rows = _rows("0.0", "", "4.0")
    result = interpolate(rows, ["score"])
    assert result.filled_count == 1


def test_interpolated_value_midpoint():
    rows = _rows("0.0", "", "4.0")
    result = interpolate(rows, ["score"])
    assert float(result.rows[1]["score"]) == pytest.approx(2.0)


def test_interpolated_value_uneven_span():
    rows = _rows("0.0", "", "", "9.0")
    result = interpolate(rows, ["score"])
    assert float(result.rows[1]["score"]) == pytest.approx(3.0)
    assert float(result.rows[2]["score"]) == pytest.approx(6.0)


def test_no_gaps_returns_unchanged():
    rows = _rows("1.0", "2.0", "3.0")
    result = interpolate(rows, ["score"])
    assert result.filled_count == 0
    assert [r["score"] for r in result.rows] == ["1.0", "2.0", "3.0"]


def test_edge_gap_left_not_filled():
    rows = _rows("", "2.0", "4.0")
    result = interpolate(rows, ["score"])
    assert result.rows[0]["score"] == ""
    assert result.filled_count == 0


def test_edge_gap_right_not_filled():
    rows = _rows("0.0", "2.0", "")
    result = interpolate(rows, ["score"])
    assert result.rows[2]["score"] == ""
    assert result.filled_count == 0


def test_multiple_columns_filled_independently():
    rows = [
        {"id": "1", "a": "0.0", "b": "10.0"},
        {"id": "2", "a": "",    "b": ""},
        {"id": "3", "a": "4.0", "b": "20.0"},
    ]
    result = interpolate(rows, ["a", "b"])
    assert float(result.rows[1]["a"]) == pytest.approx(2.0)
    assert float(result.rows[1]["b"]) == pytest.approx(15.0)
    assert result.filled_count == 2


def test_empty_rows_returns_empty_result():
    result = interpolate([], ["score"])
    assert result.rows == []
    assert result.filled_count == 0


def test_headers_preserved():
    rows = _rows("1.0", "", "3.0")
    result = interpolate(rows, ["score"])
    assert result.headers == ["id", "score"]


# ---------------------------------------------------------------------------
# error cases
# ---------------------------------------------------------------------------

def test_unknown_column_raises():
    rows = _rows("1.0", "2.0")
    with pytest.raises(InterpolatorError, match="column 'missing' not found"):
        interpolate(rows, ["missing"])


def test_empty_columns_list_raises():
    rows = _rows("1.0", "2.0")
    with pytest.raises(InterpolatorError, match="at least one column"):
        interpolate(rows, [])


def test_non_numeric_existing_values_treated_as_missing():
    rows = _rows("1.0", "abc", "3.0")
    # 'abc' cannot be parsed so it is treated as a gap
    result = interpolate(rows, ["score"])
    assert float(result.rows[1]["score"]) == pytest.approx(2.0)
