"""Tests for csvdiff.padder."""
import pytest
from csvdiff.padder import (
    PadResult,
    PadderError,
    pad_columns,
    pad_to_union,
)


@pytest.fixture
def rows():
    return [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
    ]


def test_returns_pad_result(rows):
    result = pad_columns(["id", "name"], rows, ["score"])
    assert isinstance(result, PadResult)


def test_row_count_unchanged(rows):
    result = pad_columns(["id", "name"], rows, ["score"])
    assert result.row_count == 2


def test_added_columns_recorded(rows):
    result = pad_columns(["id", "name"], rows, ["score", "grade"])
    assert result.added_columns == ["score", "grade"]


def test_added_column_count(rows):
    result = pad_columns(["id", "name"], rows, ["score", "grade"])
    assert result.added_column_count == 2


def test_headers_extended(rows):
    result = pad_columns(["id", "name"], rows, ["score"])
    assert result.headers == ["id", "name", "score"]


def test_fill_value_default_empty_string(rows):
    result = pad_columns(["id", "name"], rows, ["score"])
    assert all(r["score"] == "" for r in result.rows)


def test_fill_value_custom(rows):
    result = pad_columns(["id", "name"], rows, ["score"], fill_value="N/A")
    assert all(r["score"] == "N/A" for r in result.rows)
    assert result.fill_value == "N/A"


def test_existing_values_preserved(rows):
    result = pad_columns(["id", "name"], rows, ["score"])
    assert result.rows[0]["name"] == "Alice"
    assert result.rows[1]["id"] == "2"


def test_no_extra_columns_is_noop(rows):
    result = pad_columns(["id", "name"], rows, [])
    assert result.added_columns == []
    assert result.headers == ["id", "name"]
    assert result.row_count == 2


def test_overlap_raises(rows):
    with pytest.raises(PadderError, match="already exist"):
        pad_columns(["id", "name"], rows, ["name"])


def test_empty_headers_and_extra_raises():
    with pytest.raises(PadderError):
        pad_columns([], [], [])


def test_pad_to_union_symmetric():
    ha = ["id", "name"]
    ra = [{"id": "1", "name": "Alice"}]
    hb = ["id", "score"]
    rb = [{"id": "1", "score": "99"}]
    res_a, res_b = pad_to_union(ha, ra, hb, rb)
    assert "score" in res_a.headers
    assert "name" in res_b.headers


def test_pad_to_union_fill_value_propagated():
    ha = ["id"]
    ra = [{"id": "1"}]
    hb = ["id", "extra"]
    rb = [{"id": "1", "extra": "x"}]
    res_a, _ = pad_to_union(ha, ra, hb, rb, fill_value="-")
    assert res_a.rows[0]["extra"] == "-"


def test_pad_to_union_identical_headers_no_extra():
    h = ["id", "name"]
    r = [{"id": "1", "name": "Alice"}]
    res_a, res_b = pad_to_union(h, r, h, r)
    assert res_a.added_columns == []
    assert res_b.added_columns == []
