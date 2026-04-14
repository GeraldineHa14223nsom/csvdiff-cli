"""Unit tests for csvdiff.splitter."""
import pytest

from csvdiff.splitter import (
    SplitterError,
    SplitResult,
    chunk_to_csv,
    split_by_column,
    split_by_count,
)

ROWS = [
    {"id": "1", "region": "north", "val": "10"},
    {"id": "2", "region": "south", "val": "20"},
    {"id": "3", "region": "north", "val": "30"},
    {"id": "4", "region": "east",  "val": "40"},
    {"id": "5", "region": "south", "val": "50"},
]


def test_split_by_count_basic():
    result = split_by_count(ROWS, 2)
    assert result.chunk_count == 3
    assert len(result.chunks["1"]) == 2
    assert len(result.chunks["2"]) == 2
    assert len(result.chunks["3"]) == 1


def test_split_by_count_total_rows():
    result = split_by_count(ROWS, 2)
    assert result.total_rows == len(ROWS)


def test_split_by_count_exact_multiple():
    result = split_by_count(ROWS[:4], 2)
    assert result.chunk_count == 2


def test_split_by_count_invalid_size_raises():
    with pytest.raises(SplitterError):
        split_by_count(ROWS, 0)


def test_split_by_count_empty_rows():
    result = split_by_count([], 10)
    assert result.chunk_count == 0
    assert result.total_rows == 0


def test_split_by_column_groups_correctly():
    result = split_by_column(ROWS, "region")
    assert set(result.chunks.keys()) == {"north", "south", "east"}
    assert len(result.chunks["north"]) == 2
    assert len(result.chunks["south"]) == 2
    assert len(result.chunks["east"]) == 1


def test_split_by_column_total_rows():
    result = split_by_column(ROWS, "region")
    assert result.total_rows == len(ROWS)


def test_split_by_column_unknown_column_raises():
    with pytest.raises(SplitterError, match="not found"):
        split_by_column(ROWS, "nonexistent")


def test_split_by_column_empty_rows():
    result = split_by_column([], "region")
    assert result.chunk_count == 0


def test_chunk_to_csv_round_trip():
    csv_text = chunk_to_csv(ROWS[:2])
    import csv as csv_mod, io
    reader = csv_mod.DictReader(io.StringIO(csv_text))
    recovered = list(reader)
    assert recovered == ROWS[:2]


def test_chunk_to_csv_empty():
    assert chunk_to_csv([]) == ""
