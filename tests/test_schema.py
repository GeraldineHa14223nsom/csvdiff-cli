"""Tests for csvdiff.schema validation."""
import pytest

from csvdiff.schema import (
    SchemaError,
    SchemaResult,
    validate_columns,
)


LEFT = ["id", "name", "email", "age"]
RIGHT = ["id", "name", "email", "age"]


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def test_valid_identical_headers():
    result = validate_columns(LEFT, RIGHT, key_columns=["id"])
    assert result.valid is True
    assert result.errors == []


def test_valid_with_multiple_keys():
    result = validate_columns(LEFT, RIGHT, key_columns=["id", "name"])
    assert result.valid is True


def test_valid_non_strict_extra_column_in_right():
    right = RIGHT + ["phone"]
    result = validate_columns(LEFT, right, key_columns=["id"], strict=False)
    assert result.valid is True


# ---------------------------------------------------------------------------
# Missing key column tests
# ---------------------------------------------------------------------------

def test_key_missing_in_left():
    result = validate_columns(["name"], RIGHT, key_columns=["id"])
    assert result.valid is False
    assert any("id" in e.missing_columns for e in result.errors)


def test_key_missing_in_right():
    result = validate_columns(LEFT, ["name"], key_columns=["id"])
    assert result.valid is False
    assert any("id" in e.missing_columns for e in result.errors)


def test_multiple_keys_missing():
    result = validate_columns(["x"], ["y"], key_columns=["id", "name"])
    assert result.valid is False
    missing = [c for e in result.errors for c in e.missing_columns]
    assert "id" in missing
    assert "name" in missing


# ---------------------------------------------------------------------------
# Strict mode tests
# ---------------------------------------------------------------------------

def test_strict_mode_identical_passes():
    result = validate_columns(LEFT, RIGHT, key_columns=["id"], strict=True)
    assert result.valid is True


def test_strict_mode_extra_column_fails():
    right = RIGHT + ["phone"]
    result = validate_columns(LEFT, right, key_columns=["id"], strict=True)
    assert result.valid is False


def test_strict_mode_error_reports_columns():
    right = RIGHT + ["phone"]
    result = validate_columns(LEFT, right, key_columns=["id"], strict=True)
    combined_missing = [c for e in result.errors for c in e.missing_columns]
    assert "phone" in combined_missing


def test_strict_mode_extra_column_in_left_fails():
    """Strict mode should also flag columns present in left but absent in right."""
    left = LEFT + ["phone"]
    result = validate_columns(left, RIGHT, key_columns=["id"], strict=True)
    assert result.valid is False
    combined_missing = [c for e in result.errors for c in e.missing_columns]
    assert "phone" in combined_missing


# ---------------------------------------------------------------------------
# SchemaResult.raise_if_invalid
# ---------------------------------------------------------------------------

def test_raise_if_invalid_does_not_raise_when_valid():
    result = validate_columns(LEFT, RIGHT, key_columns=["id"])
    result.raise_if_invalid()  # should not raise


def test_raise_if_invalid_raises_schema_error():
    result = validate_columns(["name"], RIGHT, key_columns=["id"])
    with pytest.raises(SchemaError):
        result.raise_if_invalid()
