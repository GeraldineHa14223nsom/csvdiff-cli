"""Tests for csvdiff.sentinel."""
import pytest
from csvdiff.sentinel import (
    SentinelError,
    SentinelMatch,
    SentinelResult,
    sentinel,
)


@pytest.fixture
def rows():
    return [
        {"id": "1", "name": "Alice", "score": "42"},
        {"id": "2", "name": "", "score": "-5"},
        {"id": "3", "name": "Bob", "score": "abc"},
        {"id": "4", "name": "Carol", "score": "0"},
    ]


def test_returns_sentinel_result(rows):
    result = sentinel(rows, {})
    assert isinstance(result, SentinelResult)


def test_no_rules_no_matches(rows):
    result = sentinel(rows, {})
    assert result.match_count == 0


def test_nonempty_flags_blank_name(rows):
    result = sentinel(rows, {"name": "nonempty"})
    assert result.match_count == 1
    assert result.matches[0].column == "name"
    assert result.matches[0].rule == "nonempty"


def test_numeric_flags_non_numeric_score(rows):
    result = sentinel(rows, {"score": "numeric"})
    assert result.match_count == 1
    assert result.matches[0].value == "abc"


def test_positive_flags_non_positive(rows):
    result = sentinel(rows, {"score": "positive"})
    flagged_values = {m.value for m in result.matches}
    assert "-5" in flagged_values
    assert "0" in flagged_values


def test_negative_flags_non_negative(rows):
    result = sentinel(rows, {"score": "negative"})
    flagged_values = {m.value for m in result.matches}
    assert "42" in flagged_values
    assert "0" in flagged_values


def test_multiple_rules_multiple_matches(rows):
    result = sentinel(rows, {"name": "nonempty", "score": "numeric"})
    assert result.match_count == 2


def test_flagged_row_count(rows):
    result = sentinel(rows, {"name": "nonempty", "score": "positive"})
    # row 2 triggers nonempty on name AND positive on score → 1 flagged row
    # row 4 triggers positive on score → another flagged row
    assert result.flagged_row_count >= 1


def test_label_column_added(rows):
    result = sentinel(rows, {"name": "nonempty"}, label_column="_flag")
    assert all("_flag" in r for r in result.rows)


def test_label_column_blank_for_clean_rows(rows):
    result = sentinel(rows, {"name": "nonempty"}, label_column="_flag")
    clean = [r for r in result.rows if r["name"] != ""]
    assert all(r["_flag"] == "" for r in clean)


def test_label_column_shows_rule_name(rows):
    result = sentinel(rows, {"name": "nonempty"}, label_column="_flag")
    flagged = [r for r in result.rows if r["_flag"] != ""]
    assert flagged[0]["_flag"] == "nonempty"


def test_empty_rows_returns_empty_result():
    result = sentinel([], {"name": "nonempty"})
    assert result.match_count == 0
    assert result.rows == []


def test_unknown_column_raises(rows):
    with pytest.raises(SentinelError, match="not found"):
        sentinel(rows, {"missing_col": "nonempty"})


def test_unknown_rule_raises(rows):
    with pytest.raises(SentinelError, match="Unknown sentinel rule"):
        sentinel(rows, {"name": "badRule"})
