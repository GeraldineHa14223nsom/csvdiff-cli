"""Tests for csvdiff.normalizer."""

import pytest

from csvdiff.normalizer import NormalizerError, NormalizeResult, normalize_rows


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rows(*dicts):
    return list(dicts)


# ---------------------------------------------------------------------------
# strip behaviour
# ---------------------------------------------------------------------------

def test_strip_removes_whitespace():
    rows = [{"name": "  Alice ", "age": " 30 "}]
    result = normalize_rows(rows, strip=True)
    assert result.rows[0] == {"name": "Alice", "age": "30"}


def test_no_strip_preserves_whitespace():
    rows = [{"name": "  Alice "}]
    result = normalize_rows(rows, strip=False)
    assert result.rows[0]["name"] == "  Alice "


# ---------------------------------------------------------------------------
# case transformations
# ---------------------------------------------------------------------------

def test_case_lower():
    rows = [{"city": "New York"}]
    result = normalize_rows(rows, case="lower")
    assert result.rows[0]["city"] == "new york"


def test_case_upper():
    rows = [{"city": "new york"}]
    result = normalize_rows(rows, case="upper")
    assert result.rows[0]["city"] == "NEW YORK"


def test_case_title():
    rows = [{"city": "new york"}]
    result = normalize_rows(rows, case="title")
    assert result.rows[0]["city"] == "New York"


def test_invalid_case_raises():
    with pytest.raises(NormalizerError, match="Invalid case mode"):
        normalize_rows([{"a": "x"}], case="camel")


# ---------------------------------------------------------------------------
# empty_value substitution
# ---------------------------------------------------------------------------

def test_empty_value_replaced():
    rows = [{"name": "Alice", "note": ""}]
    result = normalize_rows(rows, empty_value="N/A")
    assert result.rows[0]["note"] == "N/A"


def test_non_empty_value_not_replaced():
    rows = [{"name": "Alice", "note": "hello"}]
    result = normalize_rows(rows, empty_value="N/A")
    assert result.rows[0]["note"] == "hello"


# ---------------------------------------------------------------------------
# column restriction
# ---------------------------------------------------------------------------

def test_columns_restricts_normalization():
    rows = [{"name": "  Alice ", "city": "  NYC "}]
    result = normalize_rows(rows, strip=True, columns=["name"])
    assert result.rows[0]["name"] == "Alice"
    assert result.rows[0]["city"] == "  NYC "  # untouched


def test_unknown_column_raises():
    rows = [{"name": "Alice"}]
    with pytest.raises(NormalizerError, match="Unknown columns"):
        normalize_rows(rows, columns=["nonexistent"])


# ---------------------------------------------------------------------------
# NormalizeResult counts
# ---------------------------------------------------------------------------

def test_modified_count_correct():
    rows = [
        {"name": "  Alice "},
        {"name": "Bob"},
        {"name": "  Carol "},
    ]
    result = normalize_rows(rows, strip=True)
    assert result.modified_count == 2
    assert result.original_count == 3
    assert result.unchanged_count() == 1


def test_no_changes_modified_count_zero():
    rows = [{"name": "Alice"}, {"name": "Bob"}]
    result = normalize_rows(rows, strip=True)
    assert result.modified_count == 0
    assert result.unchanged_count() == 2


def test_empty_rows_returns_empty_result():
    result = normalize_rows([])
    assert result.rows == []
    assert result.original_count == 0
    assert result.modified_count == 0
