"""Tests for csvdiff.validator."""

import pytest

from csvdiff.validator import (
    ValidationError,
    ValidationResult,
    get_rule,
    validate_rows,
)


# ---------------------------------------------------------------------------
# get_rule
# ---------------------------------------------------------------------------

def test_get_rule_nonempty_passes():
    fn = get_rule("nonempty")
    assert fn("hello") is True


def test_get_rule_nonempty_fails_blank():
    fn = get_rule("nonempty")
    assert fn("") is False
    assert fn("   ") is False


def test_get_rule_numeric_passes():
    fn = get_rule("numeric")
    assert fn("3.14") is True
    assert fn("-7") is True


def test_get_rule_numeric_fails():
    fn = get_rule("numeric")
    assert fn("abc") is False


def test_get_rule_integer_passes():
    fn = get_rule("integer")
    assert fn("42") is True
    assert fn("-1") is True


def test_get_rule_integer_fails_float():
    fn = get_rule("integer")
    assert fn("3.14") is False


def test_get_rule_ascii_passes():
    fn = get_rule("ascii")
    assert fn("hello") is True


def test_get_rule_ascii_fails():
    fn = get_rule("ascii")
    assert fn("caf\u00e9") is False


def test_get_rule_unknown_raises():
    with pytest.raises(ValidationError, match="Unknown rule"):
        get_rule("bogus")


# ---------------------------------------------------------------------------
# validate_rows
# ---------------------------------------------------------------------------

def test_validate_rows_no_violations():
    rows = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
    result = validate_rows(rows, {"name": ["nonempty"], "age": ["integer"]})
    assert result.is_valid
    assert result.violation_count() == 0


def test_validate_rows_detects_empty():
    rows = [{"name": "", "age": "30"}]
    result = validate_rows(rows, {"name": ["nonempty"]})
    assert not result.is_valid
    assert result.violations[0].column == "name"
    assert result.violations[0].rule == "nonempty"


def test_validate_rows_detects_non_integer():
    rows = [{"name": "Alice", "age": "old"}]
    result = validate_rows(rows, {"age": ["integer"]})
    assert not result.is_valid
    assert result.violations[0].row_index == 0


def test_validate_rows_multiple_violations():
    rows = [
        {"name": "", "age": "bad"},
        {"name": "Bob", "age": "25"},
    ]
    result = validate_rows(rows, {"name": ["nonempty"], "age": ["integer"]})
    assert result.violation_count() == 2


def test_validate_rows_column_filter():
    rows = [{"name": "", "age": "bad"}]
    result = validate_rows(
        rows,
        {"name": ["nonempty"], "age": ["integer"]},
        columns=["name"],
    )
    # Only 'name' should be checked
    assert result.violation_count() == 1
    assert result.violations[0].column == "name"


def test_validate_rows_missing_column_treated_as_empty():
    rows = [{"name": "Alice"}]  # 'age' key absent
    result = validate_rows(rows, {"age": ["nonempty"]})
    assert not result.is_valid


def test_validate_rows_unknown_rule_raises():
    rows = [{"name": "Alice"}]
    with pytest.raises(ValidationError, match="Unknown rule"):
        validate_rows(rows, {"name": ["nonexistent"]})
