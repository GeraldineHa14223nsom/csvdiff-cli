import pytest
from csvdiff.comparer import (
    compare, CompareResult, ComparerError,
    mismatch_count, match_rate,
)


def _rows(values):
    return [{"id": str(i), "val": str(v)} for i, v in enumerate(values)]


def test_returns_compare_result():
    r = compare(_rows([1, 2]), _rows([1, 2]), columns=["val"])
    assert isinstance(r, CompareResult)


def test_no_mismatches_when_equal():
    r = compare(_rows([1, 2, 3]), _rows([1, 2, 3]), columns=["val"])
    assert mismatch_count(r) == 0


def test_detects_mismatch():
    r = compare(_rows([1, 2]), _rows([1, 9]), columns=["val"])
    assert mismatch_count(r) == 1


def test_match_rate_perfect():
    r = compare(_rows([1, 2]), _rows([1, 2]), columns=["val"])
    assert match_rate(r) == 1.0


def test_match_rate_half():
    r = compare(_rows([1, 2]), _rows([9, 2]), columns=["val"])
    assert match_rate(r) == 0.5


def test_match_rate_empty_rows():
    r = compare([], [], columns=["val"])
    assert match_rate(r) == 1.0


def test_tolerance_allows_small_diff():
    left = [{"v": "1.0"}]
    right = [{"v": "1.004"}]
    r = compare(left, right, columns=["v"], tolerance=0.01)
    assert mismatch_count(r) == 0


def test_tolerance_rejects_large_diff():
    left = [{"v": "1.0"}]
    right = [{"v": "1.1"}]
    r = compare(left, right, columns=["v"], tolerance=0.01)
    assert mismatch_count(r) == 1


def test_empty_columns_raises():
    with pytest.raises(ComparerError):
        compare(_rows([1]), _rows([1]), columns=[])


def test_unknown_column_raises():
    with pytest.raises(ComparerError):
        compare(_rows([1]), _rows([1]), columns=["nonexistent"])


def test_columns_compared_stored():
    r = compare(_rows([1]), _rows([1]), columns=["val"])
    assert r.columns_compared == ["val"]


def test_row_contains_left_right_keys():
    r = compare([{"val": "A"}], [{"val": "B"}], columns=["val"])
    assert "val_left" in r.rows[0]
    assert "val_right" in r.rows[0]


def test_truncates_to_shorter_list():
    r = compare(_rows([1, 2, 3]), _rows([1, 2]), columns=["val"])
    assert len(r.rows) == 2
