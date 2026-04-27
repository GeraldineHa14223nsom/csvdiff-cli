"""Tests for csvdiff.extractor."""
import pytest
from csvdiff.extractor import extract, ExtractorError, ExtractResult


@pytest.fixture()
def rows():
    return [
        {"id": "1", "name": "Alice", "city": "New York"},
        {"id": "2", "name": "Bob", "city": "Los Angeles"},
        {"id": "3", "name": "Charlie", "city": "New York"},
        {"id": "4", "name": "Diana", "city": "Chicago"},
        {"id": "5", "name": "Eve", "city": ""},
    ]


HEADERS = ["id", "name", "city"]


def test_returns_extract_result(rows):
    result = extract(HEADERS, rows, "city", "New York")
    assert isinstance(result, ExtractResult)


def test_matched_count(rows):
    result = extract(HEADERS, rows, "city", "New York")
    assert result.matched_count == 2


def test_unmatched_count(rows):
    result = extract(HEADERS, rows, "city", "New York")
    assert result.unmatched_count == 3


def test_match_rate(rows):
    result = extract(HEADERS, rows, "city", "New York")
    assert result.match_rate == pytest.approx(0.4)


def test_matched_rows_correct(rows):
    result = extract(HEADERS, rows, "city", "New York")
    names = [r["name"] for r in result.rows]
    assert names == ["Alice", "Charlie"]


def test_regex_pattern(rows):
    result = extract(HEADERS, rows, "name", r"^[AB]")
    names = [r["name"] for r in result.rows]
    assert names == ["Alice", "Bob"]


def test_invert_returns_non_matching(rows):
    result = extract(HEADERS, rows, "city", "New York", invert=True)
    names = [r["name"] for r in result.rows]
    assert "Alice" not in names
    assert "Bob" in names


def test_invert_count(rows):
    result = extract(HEADERS, rows, "city", "New York", invert=True)
    assert result.matched_count == 3


def test_empty_rows():
    result = extract(HEADERS, [], "city", "New York")
    assert result.matched_count == 0
    assert result.match_rate == 0.0


def test_unknown_column_raises(rows):
    with pytest.raises(ExtractorError, match="column 'missing' not found"):
        extract(HEADERS, rows, "missing", "x")


def test_empty_pattern_raises(rows):
    with pytest.raises(ExtractorError, match="pattern must not be empty"):
        extract(HEADERS, rows, "city", "")


def test_invalid_regex_raises(rows):
    with pytest.raises(ExtractorError, match="invalid regex"):
        extract(HEADERS, rows, "city", "[unclosed")


def test_headers_preserved(rows):
    result = extract(HEADERS, rows, "city", "Chicago")
    assert result.headers == HEADERS


def test_original_count_preserved(rows):
    result = extract(HEADERS, rows, "city", "Chicago")
    assert result.original_count == 5
