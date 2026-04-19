"""Tests for csvdiff.roller."""
import pytest
from csvdiff.roller import rolling, RollerError


@pytest.fixture
def rows():
    return [
        {"id": "1", "val": "10"},
        {"id": "2", "val": "20"},
        {"id": "3", "val": "30"},
        {"id": "4", "val": "40"},
        {"id": "5", "val": "50"},
    ]


def test_rolling_mean_computed_count(rows):
    r = rolling(rows, "val", window=3)
    assert r.computed == 3


def test_rolling_mean_empty_prefix(rows):
    r = rolling(rows, "val", window=3)
    assert r.rows[0][r.new_column] == ""
    assert r.rows[1][r.new_column] == ""


def test_rolling_mean_values(rows):
    r = rolling(rows, "val", window=3)
    assert float(r.rows[2][r.new_column]) == pytest.approx(20.0)
    assert float(r.rows[3][r.new_column]) == pytest.approx(30.0)
    assert float(r.rows[4][r.new_column]) == pytest.approx(40.0)


def test_rolling_sum(rows):
    r = rolling(rows, "val", window=2, func="sum")
    assert float(r.rows[1][r.new_column]) == pytest.approx(30.0)


def test_rolling_min(rows):
    r = rolling(rows, "val", window=2, func="min")
    assert float(r.rows[4][r.new_column]) == pytest.approx(40.0)


def test_rolling_max(rows):
    r = rolling(rows, "val", window=2, func="max")
    assert float(r.rows[4][r.new_column]) == pytest.approx(50.0)


def test_custom_new_column_name(rows):
    r = rolling(rows, "val", window=2, new_column="my_col")
    assert r.new_column == "my_col"
    assert "my_col" in r.rows[0]


def test_default_column_name(rows):
    r = rolling(rows, "val", window=3)
    assert r.new_column == "val_rolling_mean_3"


def test_invalid_window_raises(rows):
    with pytest.raises(RollerError):
        rolling(rows, "val", window=0)


def test_unknown_column_raises(rows):
    with pytest.raises(RollerError):
        rolling(rows, "missing", window=2)


def test_unknown_func_raises(rows):
    with pytest.raises(RollerError):
        rolling(rows, "val", window=2, func="median")


def test_non_numeric_value_raises():
    rows = [{"val": "abc"}, {"val": "10"}]
    with pytest.raises(RollerError):
        rolling(rows, "val", window=2)


def test_empty_rows():
    r = rolling([], "val", window=3)
    assert r.rows == []
    assert r.computed == 0


def test_window_one(rows):
    r = rolling(rows, "val", window=1)
    assert r.computed == 5
    assert float(r.rows[0][r.new_column]) == pytest.approx(10.0)
