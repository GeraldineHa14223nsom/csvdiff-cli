"""Tests for csvdiff.tagger."""
import pytest
from csvdiff.tagger import TaggerError, TagResult, tag_rows


@pytest.fixture
def rows():
    return [
        {"id": "1", "country": "US", "score": "10"},
        {"id": "2", "country": "GB", "score": "20"},
        {"id": "3", "country": "DE", "score": "30"},
        {"id": "4", "country": "US", "score": "40"},
    ]


def test_returns_tag_result(rows):
    result = tag_rows(rows, column="country", values={"US"})
    assert isinstance(result, TagResult)


def test_tagged_count(rows):
    result = tag_rows(rows, column="country", values={"US"})
    assert result.tagged_count == 2


def test_untagged_count(rows):
    result = tag_rows(rows, column="country", values={"US"})
    assert result.untagged_count == 2


def test_tag_column_added(rows):
    result = tag_rows(rows, column="country", values={"US"})
    assert "tag" in result.headers
    assert all("tag" in r for r in result.rows)


def test_custom_tag_column(rows):
    result = tag_rows(rows, column="country", values={"US"}, tag_column="region_flag")
    assert result.tag_column == "region_flag"
    assert "region_flag" in result.headers


def test_match_label_applied(rows):
    result = tag_rows(rows, column="country", values={"US"}, match_label="yes")
    matched = [r for r in result.rows if r["country"] == "US"]
    assert all(r["tag"] == "yes" for r in matched)


def test_no_match_label_applied(rows):
    result = tag_rows(rows, column="country", values={"US"}, no_match_label="no")
    unmatched = [r for r in result.rows if r["country"] != "US"]
    assert all(r["tag"] == "no" for r in unmatched)


def test_multiple_values_in_set(rows):
    result = tag_rows(rows, column="country", values={"US", "GB"})
    assert result.tagged_count == 3
    assert result.untagged_count == 1


def test_empty_rows_returns_empty_result():
    result = tag_rows([], column="country", values={"US"})
    assert result.rows == []
    assert result.tagged_count == 0
    assert result.untagged_count == 0


def test_unknown_column_raises(rows):
    with pytest.raises(TaggerError, match="not found"):
        tag_rows(rows, column="nonexistent", values={"US"})


def test_existing_tag_column_raises(rows):
    with pytest.raises(TaggerError, match="already exists"):
        tag_rows(rows, column="country", values={"US"}, tag_column="country")


def test_original_values_preserved(rows):
    result = tag_rows(rows, column="country", values={"US"})
    for orig, tagged in zip(rows, result.rows):
        assert tagged["id"] == orig["id"]
        assert tagged["score"] == orig["score"]
