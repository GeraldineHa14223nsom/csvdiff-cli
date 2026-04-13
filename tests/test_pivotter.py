"""Tests for csvdiff.pivotter."""
import pytest

from csvdiff.pivotter import PivotError, PivotResult, pivot


ROWS = [
    {"region": "North", "product": "A", "sales": "10"},
    {"region": "North", "product": "B", "sales": "20"},
    {"region": "South", "product": "A", "sales": "30"},
    {"region": "South", "product": "A", "sales": "5"},
    {"region": "South", "product": "B", "sales": "15"},
]


def test_pivot_returns_pivot_result():
    result = pivot(ROWS, "region", "product", "sales")
    assert isinstance(result, PivotResult)


def test_pivot_col_order_preserved():
    result = pivot(ROWS, "region", "product", "sales")
    assert result.col_order == ["A", "B"]


def test_pivot_sum_aggregation():
    result = pivot(ROWS, "region", "product", "sales", aggregation="sum")
    assert result.table["North"]["A"] == 10.0
    assert result.table["North"]["B"] == 20.0
    assert result.table["South"]["A"] == 35.0  # 30 + 5
    assert result.table["South"]["B"] == 15.0


def test_pivot_count_aggregation():
    result = pivot(ROWS, "region", "product", "sales", aggregation="count")
    assert result.table["South"]["A"] == 2.0
    assert result.table["North"]["A"] == 1.0


def test_pivot_mean_aggregation():
    result = pivot(ROWS, "region", "product", "sales", aggregation="mean")
    assert result.table["South"]["A"] == pytest.approx(17.5)


def test_pivot_min_aggregation():
    result = pivot(ROWS, "region", "product", "sales", aggregation="min")
    assert result.table["South"]["A"] == 5.0


def test_pivot_max_aggregation():
    result = pivot(ROWS, "region", "product", "sales", aggregation="max")
    assert result.table["South"]["A"] == 30.0


def test_pivot_empty_rows_returns_empty_table():
    result = pivot([], "region", "product", "sales")
    assert result.table == {}
    assert result.col_order == []


def test_pivot_unknown_aggregation_raises():
    with pytest.raises(PivotError, match="Unknown aggregation"):
        pivot(ROWS, "region", "product", "sales", aggregation="median")


def test_pivot_missing_row_field_raises():
    with pytest.raises(PivotError, match="Column 'missing'"):
        pivot(ROWS, "missing", "product", "sales")


def test_pivot_missing_value_field_raises():
    with pytest.raises(PivotError, match="Column 'revenue'"):
        pivot(ROWS, "region", "product", "revenue")


def test_pivot_non_numeric_value_raises():
    bad_rows = [{"region": "North", "product": "A", "sales": "n/a"}]
    with pytest.raises(PivotError, match="Cannot convert value"):
        pivot(bad_rows, "region", "product", "sales")


def test_pivot_metadata_stored():
    result = pivot(ROWS, "region", "product", "sales", aggregation="max")
    assert result.row_field == "region"
    assert result.col_field == "product"
    assert result.value_field == "sales"
    assert result.aggregation == "max"
