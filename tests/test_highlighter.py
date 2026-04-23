"""Tests for csvdiff.highlighter."""

import pytest

from csvdiff.highlighter import (
    HighlighterError,
    HighlightResult,
    highlight,
    match_rate,
)


@pytest.fixture()
def rows():
    return [
        {"id": "1", "name": "Alice", "email": "alice@example.com"},
        {"id": "2", "name": "Bob", "email": "bob@corp.org"},
        {"id": "3", "name": "Charlie", "email": "charlie@example.com"},
        {"id": "4", "name": "Diana", "email": "diana@other.net"},
    ]


def test_returns_highlight_result(rows):
    result = highlight(rows, "email", r"example\.com")
    assert isinstance(result, HighlightResult)


def test_match_count_correct(rows):
    result = highlight(rows, "email", r"example\.com")
    assert result.match_count == 2


def test_flagged_rows_contain_matches(rows):
    result = highlight(rows, "email", r"example\.com")
    emails = [r["email"] for r in result.flagged]
    assert "alice@example.com" in emails
    assert "charlie@example.com" in emails


def test_highlight_column_added(rows):
    result = highlight(rows, "email", r"example\.com")
    assert all("_highlight" in r for r in result.rows)


def test_highlight_column_values(rows):
    result = highlight(rows, "email", r"example\.com")
    values = {r["email"]: r["_highlight"] for r in result.rows}
    assert values["alice@example.com"] == "1"
    assert values["bob@corp.org"] == "0"


def test_custom_highlight_column_name(rows):
    result = highlight(rows, "name", r"^A", highlight_column="matched")
    assert all("matched" in r for r in result.rows)


def test_case_insensitive_by_default(rows):
    result = highlight(rows, "name", r"alice")
    assert result.match_count == 1


def test_case_sensitive_flag(rows):
    result = highlight(rows, "name", r"alice", case_sensitive=True)
    assert result.match_count == 0


def test_match_rate(rows):
    result = highlight(rows, "email", r"example\.com")
    assert match_rate(result) == pytest.approx(0.5)


def test_match_rate_empty_rows():
    result = highlight([], "email", r"example\.com")
    assert match_rate(result) == 0.0


def test_unknown_column_raises(rows):
    with pytest.raises(HighlighterError, match="Column 'missing'"):
        highlight(rows, "missing", r".*")


def test_invalid_regex_raises(rows):
    with pytest.raises(HighlighterError, match="Invalid regex"):
        highlight(rows, "name", r"[unclosed")


def test_original_rows_unchanged(rows):
    highlight(rows, "name", r"Alice")
    assert "_highlight" not in rows[0]


def test_all_rows_preserved(rows):
    result = highlight(rows, "name", r"Alice")
    assert len(result.rows) == len(rows)
