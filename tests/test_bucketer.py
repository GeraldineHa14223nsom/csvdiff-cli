"""Tests for csvdiff.bucketer."""
import pytest
from csvdiff.bucketer import BucketerError, BucketResult, bucket_rows


@pytest.fixture()
def rows():
    return [
        {"name": "Alice", "score": "25"},
        {"name": "Bob", "score": "55"},
        {"name": "Carol", "score": "75"},
        {"name": "Dave", "score": "95"},
        {"name": "Eve", "score": "abc"},
    ]


BUCKETS = [("low", 0, 50), ("mid", 50, 75), ("high", 75, 100)]


def test_returns_bucket_result(rows):
    result = bucket_rows(rows, "score", BUCKETS)
    assert isinstance(result, BucketResult)


def test_row_count_unchanged(rows):
    result = bucket_rows(rows, "score", BUCKETS)
    assert result.row_count == len(rows)


def test_label_column_added(rows):
    result = bucket_rows(rows, "score", BUCKETS)
    assert "bucket" in result.headers
    assert all("bucket" in r for r in result.rows)


def test_custom_label_column(rows):
    result = bucket_rows(rows, "score", BUCKETS, label_column="tier")
    assert "tier" in result.headers


def test_bucket_assignments_correct(rows):
    result = bucket_rows(rows, "score", BUCKETS)
    labels = {r["name"]: r["bucket"] for r in result.rows}
    assert labels["Alice"] == "low"
    assert labels["Bob"] == "mid"
    assert labels["Carol"] == "high"
    assert labels["Dave"] == "high"


def test_non_numeric_gets_default_label(rows):
    result = bucket_rows(rows, "score", BUCKETS)
    eve = next(r for r in result.rows if r["name"] == "Eve")
    assert eve["bucket"] == "other"


def test_custom_default_label(rows):
    result = bucket_rows(rows, "score", BUCKETS, default_label="unknown")
    eve = next(r for r in result.rows if r["name"] == "Eve")
    assert eve["bucket"] == "unknown"


def test_bucket_counts_sum_to_row_count(rows):
    result = bucket_rows(rows, "score", BUCKETS)
    assert sum(result.bucket_counts.values()) == result.row_count


def test_bucket_count_property(rows):
    result = bucket_rows(rows, "score", BUCKETS)
    assert result.bucket_count == len(result.bucket_counts)


def test_unknown_column_raises(rows):
    with pytest.raises(BucketerError, match="not found"):
        bucket_rows(rows, "nonexistent", BUCKETS)


def test_empty_buckets_raises(rows):
    with pytest.raises(BucketerError, match="At least one bucket"):
        bucket_rows(rows, "score", [])


def test_invalid_range_raises(rows):
    with pytest.raises(BucketerError, match="must be less than"):
        bucket_rows(rows, "score", [("bad", 100, 50)])


def test_empty_rows_returns_empty_result():
    result = bucket_rows([], "score", BUCKETS)
    assert result.row_count == 0
    assert result.bucket_counts == {}
