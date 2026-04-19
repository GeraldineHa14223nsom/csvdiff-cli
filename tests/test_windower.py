"""Tests for csvdiff.windower."""
import pytest
from csvdiff.windower import window_lag, windowed_row_count, WindowError


def _rows():
    return [
        {"id": "1", "val": "10"},
        {"id": "2", "val": "20"},
        {"id": "3", "val": "30"},
        {"id": "4", "val": "40"},
    ]


def test_lag1_first_row_gets_fill():
    result = window_lag(_rows(), column="val", lag=1, fill="")
    assert result.rows[0]["val_lag1"] == ""


def test_lag1_second_row_gets_first_value():
    result = window_lag(_rows(), column="val", lag=1, fill="")
    assert result.rows[1]["val_lag1"] == "10"


def test_lag1_all_values():
    result = window_lag(_rows(), column="val", lag=1, fill="0")
    lagged = [r["val_lag1"] for r in result.rows]
    assert lagged == ["0", "10", "20", "30"]


def test_lag2_fills_first_two():
    result = window_lag(_rows(), column="val", lag=2, fill="X")
    assert result.rows[0]["val_lag2"] == "X"
    assert result.rows[1]["val_lag2"] == "X"
    assert result.rows[2]["val_lag2"] == "10"


def test_custom_new_column_name():
    result = window_lag(_rows(), column="val", lag=1, new_column="prev_val")
    assert "prev_val" in result.rows[0]


def test_original_columns_preserved():
    result = window_lag(_rows(), column="val", lag=1)
    assert "id" in result.rows[0]
    assert "val" in result.rows[0]


def test_windowed_row_count():
    result = window_lag(_rows(), column="val", lag=1)
    assert windowed_row_count(result) == 4


def test_unknown_column_raises():
    with pytest.raises(WindowError, match="not found"):
        window_lag(_rows(), column="missing", lag=1)


def test_lag_zero_raises():
    with pytest.raises(WindowError, match="Lag must be"):
        window_lag(_rows(), column="val", lag=0)


def test_empty_rows_returns_empty():
    result = window_lag([], column="val", lag=1)
    assert result.rows == []


def test_result_stores_metadata():
    result = window_lag(_rows(), column="val", lag=2, fill="N/A")
    assert result.lag == 2
    assert result.fill == "N/A"
    assert result.column == "val"
