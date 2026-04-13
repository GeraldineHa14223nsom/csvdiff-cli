"""Tests for csvdiff.transform module."""

import pytest

from csvdiff.transform import (
    TransformError,
    apply_transforms,
    get_transform,
    rename_columns,
)


ROWS = [
    {"id": "1", "name": "Alice", "score": "42"},
    {"id": "2", "name": "Bob", "score": "7"},
]


# ---------------------------------------------------------------------------
# get_transform
# ---------------------------------------------------------------------------

def test_get_transform_upper():
    fn = get_transform("upper")
    assert fn("hello") == "HELLO"


def test_get_transform_lower():
    fn = get_transform("lower")
    assert fn("WORLD") == "world"


def test_get_transform_strip():
    fn = get_transform("strip")
    assert fn("  hi  ") == "hi"


def test_get_transform_unknown_raises():
    with pytest.raises(TransformError, match="Unknown transform"):
        get_transform("nonexistent")


# ---------------------------------------------------------------------------
# apply_transforms
# ---------------------------------------------------------------------------

def test_apply_transforms_upper():
    result = apply_transforms(ROWS, {"name": "upper"})
    assert result[0]["name"] == "ALICE"
    assert result[1]["name"] == "BOB"


def test_apply_transforms_int_normalises():
    result = apply_transforms(ROWS, {"score": "int"})
    assert result[0]["score"] == "42"


def test_apply_transforms_skips_missing_column():
    result = apply_transforms(ROWS, {"missing": "upper"})
    # No error; column simply absent in rows
    assert result[0] == ROWS[0]


def test_apply_transforms_bad_value_raises():
    rows = [{"id": "1", "score": "not_a_number"}]
    with pytest.raises(TransformError, match="Transform failed"):
        apply_transforms(rows, {"score": "int"})


def test_apply_transforms_unknown_transform_raises():
    with pytest.raises(TransformError, match="Unknown transform"):
        apply_transforms(ROWS, {"name": "bogus"})


def test_apply_transforms_does_not_mutate_original():
    original = [{"id": "1", "name": "Alice"}]
    apply_transforms(original, {"name": "upper"})
    assert original[0]["name"] == "Alice"


# ---------------------------------------------------------------------------
# rename_columns
# ---------------------------------------------------------------------------

def test_rename_columns_basic():
    result = rename_columns(ROWS, {"name": "full_name"})
    assert "full_name" in result[0]
    assert "name" not in result[0]


def test_rename_columns_no_rename_passthrough():
    result = rename_columns(ROWS, {})
    assert result[0] == ROWS[0]


def test_rename_columns_preserves_other_keys():
    result = rename_columns(ROWS, {"name": "full_name"})
    assert result[0]["id"] == "1"
    assert result[0]["score"] == "42"


def test_rename_columns_does_not_mutate_original():
    original = [{"id": "1", "name": "Alice"}]
    rename_columns(original, {"name": "full_name"})
    assert "name" in original[0]
