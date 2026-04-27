"""Tests for csvdiff.capper."""
import pytest
from csvdiff.capper import cap_rows, CapResult, CapperError


@pytest.fixture()
def rows():
    return [
        {"dept": "eng", "name": "Alice"},
        {"dept": "eng", "name": "Bob"},
        {"dept": "eng", "name": "Carol"},
        {"dept": "hr", "name": "Dave"},
        {"dept": "hr", "name": "Eve"},
        {"dept": "sales", "name": "Frank"},
    ]


def test_returns_cap_result(rows):
    result = cap_rows(rows, "dept", cap=2)
    assert isinstance(result, CapResult)


def test_original_count_preserved(rows):
    result = cap_rows(rows, "dept", cap=2)
    assert result.original_count == 6


def test_capped_count_correct(rows):
    result = cap_rows(rows, "dept", cap=2)
    # eng: 2, hr: 2, sales: 1 => 5
    assert result.capped_count == 5


def test_removed_count(rows):
    result = cap_rows(rows, "dept", cap=2)
    assert result.removed_count == 1


def test_rows_per_group_do_not_exceed_cap(rows):
    cap = 1
    result = cap_rows(rows, "dept", cap=cap)
    from collections import Counter
    counts = Counter(r["dept"] for r in result.rows)
    assert all(v <= cap for v in counts.values())


def test_cap_larger_than_group_keeps_all(rows):
    result = cap_rows(rows, "dept", cap=10)
    assert result.capped_count == 6
    assert result.removed_count == 0


def test_group_sizes_reflect_original_counts(rows):
    result = cap_rows(rows, "dept", cap=2)
    assert result.group_sizes == {"eng": 3, "hr": 2, "sales": 1}


def test_cap_one_keeps_first_row_per_group(rows):
    result = cap_rows(rows, "dept", cap=1)
    names = [r["name"] for r in result.rows]
    assert names == ["Alice", "Dave", "Frank"]


def test_empty_rows_returns_empty_result():
    result = cap_rows([], "dept", cap=2)
    assert result.rows == []
    assert result.original_count == 0
    assert result.capped_count == 0


def test_invalid_cap_raises():
    with pytest.raises(CapperError):
        cap_rows([{"dept": "eng"}], "dept", cap=0)


def test_unknown_column_raises():
    with pytest.raises(CapperError, match="column 'missing'"):
        cap_rows([{"dept": "eng"}], "missing", cap=1)


def test_group_column_stored(rows):
    result = cap_rows(rows, "dept", cap=2)
    assert result.group_column == "dept"


def test_cap_stored(rows):
    result = cap_rows(rows, "dept", cap=3)
    assert result.cap == 3
