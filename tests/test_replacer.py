"""Tests for csvdiff.replacer."""
import pytest
from csvdiff.replacer import (
    ReplaceResult,
    ReplacerError,
    replace_values,
)


@pytest.fixture()
def rows():
    return [
        {"id": "1", "name": "Alice Smith", "city": "New York"},
        {"id": "2", "name": "Bob Jones", "city": "new york"},
        {"id": "3", "name": "Carol", "city": "Boston"},
    ]


def test_returns_replace_result(rows):
    result = replace_values(rows, "city", "New York", "NYC")
    assert isinstance(result, ReplaceResult)


def test_row_count_unchanged(rows):
    result = replace_values(rows, "city", "New York", "NYC")
    assert result.row_count == 3


def test_simple_replacement(rows):
    result = replace_values(rows, "city", "New York", "NYC")
    assert result.rows[0]["city"] == "NYC"


def test_non_matching_row_unchanged(rows):
    result = replace_values(rows, "city", "New York", "NYC")
    assert result.rows[2]["city"] == "Boston"


def test_replaced_count_exact(rows):
    result = replace_values(rows, "city", "New York", "NYC")
    assert result.replaced_count == 1


def test_case_insensitive_replacement(rows):
    result = replace_values(rows, "city", "new york", "NYC", case_sensitive=False)
    assert result.rows[0]["city"] == "NYC"
    assert result.rows[1]["city"] == "NYC"
    assert result.replaced_count == 2


def test_regex_replacement(rows):
    result = replace_values(rows, "name", r"\bSmith\b", "S.", regex=True)
    assert result.rows[0]["name"] == "Alice S."
    assert result.replaced_count == 1


def test_regex_case_insensitive(rows):
    result = replace_values(
        rows, "name", r"alice", "ALICE", regex=True, case_sensitive=False
    )
    assert result.rows[0]["name"] == "ALICE Smith"
    assert result.replaced_count == 1


def test_other_columns_preserved(rows):
    result = replace_values(rows, "city", "New York", "NYC")
    assert result.rows[0]["id"] == "1"
    assert result.rows[0]["name"] == "Alice Smith"


def test_column_attribute_stored(rows):
    result = replace_values(rows, "city", "New York", "NYC")
    assert result.column == "city"


def test_headers_preserved(rows):
    result = replace_values(rows, "city", "New York", "NYC")
    assert result.headers == ["id", "name", "city"]


def test_unknown_column_raises(rows):
    with pytest.raises(ReplacerError):
        replace_values(rows, "country", "x", "y")


def test_empty_rows_returns_zero_replaced():
    result = replace_values([], "city", "x", "y")
    assert result.replaced_count == 0
    assert result.row_count == 0


def test_no_match_replaced_count_zero(rows):
    result = replace_values(rows, "city", "London", "LON")
    assert result.replaced_count == 0
