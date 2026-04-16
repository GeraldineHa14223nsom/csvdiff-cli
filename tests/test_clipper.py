"""Tests for csvdiff.clipper."""
import pytest
from csvdiff.clipper import clip_column, ClipperError


def _rows(*values):
    return [{"id": str(i + 1), "val": str(v)} for i, v in enumerate(values)]


def test_clip_low_clamps_small_values():
    result = clip_column(_rows(-5, 0, 10), "val", low=0)
    assert result.rows[0]["val"] == "0"
    assert result.rows[1]["val"] == "0"
    assert result.rows[2]["val"] == "10"


def test_clip_high_clamps_large_values():
    result = clip_column(_rows(1, 50, 100), "val", high=50)
    assert result.rows[1]["val"] == "50"
    assert result.rows[2]["val"] == "50"


def test_clip_both_bounds():
    result = clip_column(_rows(-10, 5, 200), "val", low=0, high=100)
    assert result.rows[0]["val"] == "0"
    assert result.rows[1]["val"] == "5"
    assert result.rows[2]["val"] == "100"


def test_clipped_count():
    result = clip_column(_rows(-1, 2, 3, 999), "val", low=0, high=10)
    assert result.clipped_count == 2


def test_no_clip_needed():
    result = clip_column(_rows(1, 2, 3), "val", low=0, high=10)
    assert result.clipped_count == 0


def test_non_numeric_cells_unchanged():
    rows = [{"id": "1", "val": "n/a"}, {"id": "2", "val": "5"}]
    result = clip_column(rows, "val", low=0, high=10)
    assert result.rows[0]["val"] == "n/a"
    assert result.clipped_count == 0


def test_original_count():
    result = clip_column(_rows(1, 2, 3), "val", low=0)
    assert result.original_count == 3


def test_unknown_column_raises():
    with pytest.raises(ClipperError, match="not found"):
        clip_column(_rows(1, 2), "missing", low=0)


def test_invalid_bounds_raises():
    with pytest.raises(ClipperError, match="low"):
        clip_column(_rows(1, 2), "val", low=10, high=5)


def test_empty_rows_returns_empty():
    result = clip_column([], "val", low=0, high=10)
    assert result.rows == []
    assert result.clipped_count == 0


def test_float_values_preserved():
    rows = [{"id": "1", "val": "3.7"}]
    result = clip_column(rows, "val", low=0, high=10)
    assert result.rows[0]["val"] == "3.7"
