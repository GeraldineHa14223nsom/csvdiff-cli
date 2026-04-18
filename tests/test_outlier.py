"""Tests for csvdiff.outlier."""
import pytest
from csvdiff.outlier import detect_outliers, OutlierError


def _rows(values):
    return [{"id": str(i), "val": str(v)} for i, v in enumerate(values)]


def test_zscore_no_outliers():
    rows = _rows([10, 11, 10, 12, 10, 11])
    result = detect_outliers(rows, "val", method="zscore", threshold=3.0)
    assert result.outlier_count() == 0


def test_zscore_detects_outlier():
    rows = _rows([10, 10, 10, 10, 10, 1000])
    result = detect_outliers(rows, "val", method="zscore", threshold=2.0)
    assert result.outlier_count() == 1
    assert result.outlier_rows[0]["val"] == "1000"


def test_iqr_detects_outlier():
    rows = _rows([1, 2, 3, 4, 5, 6, 7, 8, 9, 200])
    result = detect_outliers(rows, "val", method="iqr", threshold=1.5)
    assert result.outlier_count() >= 1
    assert any(r["val"] == "200" for r in result.outlier_rows)


def test_iqr_no_outliers():
    rows = _rows([1, 2, 3, 4, 5])
    result = detect_outliers(rows, "val", method="iqr", threshold=3.0)
    assert result.outlier_count() == 0


def test_total_rows():
    rows = _rows([1, 2, 3, 4, 5])
    result = detect_outliers(rows, "val")
    assert result.total_rows() == 5


def test_unknown_method_raises():
    rows = _rows([1, 2, 3])
    with pytest.raises(OutlierError, match="Unknown method"):
        detect_outliers(rows, "val", method="median")


def test_missing_column_raises():
    rows = _rows([1, 2, 3])
    with pytest.raises(OutlierError, match="not found"):
        detect_outliers(rows, "missing")


def test_non_numeric_raises():
    rows = [{"val": "abc"}]
    with pytest.raises(OutlierError, match="Non-numeric"):
        detect_outliers(rows, "val")


def test_empty_rows_raises():
    with pytest.raises(OutlierError, match="No rows"):
        detect_outliers([], "val")


def test_constant_column_no_outliers():
    rows = _rows([5, 5, 5, 5, 5])
    result = detect_outliers(rows, "val", method="zscore")
    assert result.outlier_count() == 0


def test_result_stores_method_and_threshold():
    rows = _rows([1, 2, 3])
    result = detect_outliers(rows, "val", method="iqr", threshold=2.5)
    assert result.method == "iqr"
    assert result.threshold == 2.5
    assert result.column == "val"
