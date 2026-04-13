"""Tests for csvdiff.deduplicator."""

import pytest

from csvdiff.deduplicator import (
    DedupeResult,
    DeduplicatorError,
    deduplicate,
    find_duplicate_keys,
)

ROWS = [
    {"id": "1", "name": "Alice", "score": "90"},
    {"id": "2", "name": "Bob",   "score": "85"},
    {"id": "1", "name": "Alice", "score": "95"},  # duplicate of first
    {"id": "3", "name": "Carol", "score": "88"},
    {"id": "2", "name": "Bob",   "score": "80"},  # duplicate of second
]


def test_deduplicate_keep_first_unique_count():
    result = deduplicate(ROWS, keys=["id"])
    assert result.unique_count == 3


def test_deduplicate_keep_first_preserves_first_occurrence():
    result = deduplicate(ROWS, keys=["id"])
    scores = {r["id"]: r["score"] for r in result.unique}
    assert scores["1"] == "90"
    assert scores["2"] == "85"


def test_deduplicate_keep_first_duplicate_count():
    result = deduplicate(ROWS, keys=["id"])
    assert result.duplicate_count == 2


def test_deduplicate_keep_last_preserves_last_occurrence():
    result = deduplicate(ROWS, keys=["id"], keep="last")
    scores = {r["id"]: r["score"] for r in result.unique}
    assert scores["1"] == "95"
    assert scores["2"] == "80"


def test_deduplicate_keep_last_duplicate_count():
    result = deduplicate(ROWS, keys=["id"], keep="last")
    assert result.duplicate_count == 2


def test_deduplicate_no_duplicates():
    unique_rows = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
    result = deduplicate(unique_rows, keys=["id"])
    assert result.unique_count == 3
    assert result.duplicate_count == 0


def test_deduplicate_empty_rows():
    result = deduplicate([], keys=["id"])
    assert result.unique == []
    assert result.duplicates == []


def test_deduplicate_invalid_keep_raises():
    with pytest.raises(DeduplicatorError, match="Invalid keep strategy"):
        deduplicate(ROWS, keys=["id"], keep="middle")


def test_deduplicate_missing_key_column_raises():
    rows = [{"id": "1"}, {"name": "Bob"}]
    with pytest.raises(DeduplicatorError, match="Key column"):
        deduplicate(rows, keys=["id"])


def test_deduplicate_composite_key():
    rows = [
        {"a": "1", "b": "x", "v": "first"},
        {"a": "1", "b": "y", "v": "second"},
        {"a": "1", "b": "x", "v": "dup"},
    ]
    result = deduplicate(rows, keys=["a", "b"])
    assert result.unique_count == 2
    assert result.duplicate_count == 1


def test_find_duplicate_keys_returns_only_dupes():
    groups = find_duplicate_keys(ROWS, keys=["id"])
    assert set(groups.keys()) == {("1",), ("2",)}


def test_find_duplicate_keys_counts():
    groups = find_duplicate_keys(ROWS, keys=["id"])
    assert len(groups[("1",)]) == 2
    assert len(groups[("2",)]) == 2


def test_find_duplicate_keys_no_dupes_returns_empty():
    rows = [{"id": "1"}, {"id": "2"}]
    groups = find_duplicate_keys(rows, keys=["id"])
    assert groups == {}
