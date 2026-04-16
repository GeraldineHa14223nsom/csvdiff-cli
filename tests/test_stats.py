"""Tests for csvdiff.stats module."""
import pytest
from csvdiff.core import DiffResult
from csvdiff.stats import DiffStats, compute_stats, format_stats_text


@pytest.fixture()
def result():
    return DiffResult(
        added=[
            {"id": "3", "name": "Charlie"},
        ],
        removed=[
            {"id": "2", "name": "Bob"},
        ],
        modified=[
            (
                {"id": "1", "name": "Alice"},
                {"id": "1", "name": "Alicia"},
            )
        ],
        unchanged=[
            {"id": "4", "name": "Diana"},
            {"id": "5", "name": "Eve"},
        ],
    )


@pytest.fixture()
def empty_result():
    return DiffResult(added=[], removed=[], modified=[], unchanged=[])


def test_compute_stats_counts(result):
    stats = compute_stats(result)
    assert stats.added == 1
    assert stats.removed == 1
    assert stats.modified == 1
    assert stats.unchanged == 2


def test_total_changes(result):
    stats = compute_stats(result)
    assert stats.total_changes == 3


def test_total_rows(result):
    stats = compute_stats(result)
    assert stats.total_rows == 5


def test_change_rate(result):
    stats = compute_stats(result)
    assert stats.change_rate == pytest.approx(0.6)


def test_change_rate_no_rows(empty_result):
    stats = compute_stats(empty_result)
    assert stats.change_rate == 0.0


def test_total_rows_no_rows(empty_result):
    stats = compute_stats(empty_result)
    assert stats.total_rows == 0


def test_total_changes_no_rows(empty_result):
    stats = compute_stats(empty_result)
    assert stats.total_changes == 0


def test_as_dict_keys(result):
    stats = compute_stats(result)
    d = stats.as_dict()
    assert set(d.keys()) == {
        "added", "removed", "modified", "unchanged",
        "total_changes", "total_rows", "change_rate",
    }


def test_as_dict_values(result):
    stats = compute_stats(result)
    d = stats.as_dict()
    assert d["added"] == 1
    assert d["total_changes"] == 3
    assert d["change_rate"] == pytest.approx(0.6, abs=1e-4)


def test_format_stats_text_contains_counts(result):
    stats = compute_stats(result)
    text = format_stats_text(stats)
    assert "Added   : 1" in text
    assert "Removed : 1" in text
    assert "Modified: 1" in text
    assert "Unchanged: 2" in text


def test_format_stats_text_contains_rate(result):
    stats = compute_stats(result)
    text = format_stats_text(stats)
    assert "60.0%" in text


def test_format_stats_text_zero_change_rate(empty_result):
    stats = compute_stats(empty_result)
    text = format_stats_text(stats)
    assert "0.0%" in text


def test_frozen_dataclass():
    stats = DiffStats(added=1, removed=0, modified=0, unchanged=0)
    with pytest.raises(Exception):
        stats.added = 99  # type: ignore[misc]
