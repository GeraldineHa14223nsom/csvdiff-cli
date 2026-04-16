"""Tests for csvdiff.anonymizer."""
import pytest
from csvdiff.anonymizer import anonymize, AnonymizerError, _hash_value, _mask_value


@pytest.fixture
def rows():
    return [
        {"id": "1", "name": "Alice", "email": "alice@example.com"},
        {"id": "2", "name": "Bob", "email": "bob@example.com"},
    ]


def test_hash_changes_value(rows):
    result = anonymize(rows, ["email"])
    assert result.rows[0]["email"] != "alice@example.com"


def test_hash_preserves_other_columns(rows):
    result = anonymize(rows, ["email"])
    assert result.rows[0]["name"] == "Alice"


def test_hash_deterministic(rows):
    r1 = anonymize(rows, ["email"])
    r2 = anonymize(rows, ["email"])
    assert r1.rows[0]["email"] == r2.rows[0]["email"]


def test_hash_with_salt_differs(rows):
    r1 = anonymize(rows, ["email"], salt="abc")
    r2 = anonymize(rows, ["email"], salt="xyz")
    assert r1.rows[0]["email"] != r2.rows[0]["email"]


def test_mask_replaces_with_stars(rows):
    result = anonymize(rows, ["name"], method="mask")
    assert result.rows[0]["name"] == "*****"


def test_mask_keep_preserves_prefix(rows):
    result = anonymize(rows, ["name"], method="mask", keep=2)
    assert result.rows[0]["name"].startswith("Al")
    assert "*" in result.rows[0]["name"]


def test_mask_custom_char(rows):
    result = anonymize(rows, ["name"], method="mask", mask_char="X")
    assert result.rows[0]["name"] == "XXXXX"


def test_unknown_column_raises(rows):
    with pytest.raises(AnonymizerError, match="Unknown columns"):
        anonymize(rows, ["nonexistent"])


def test_unknown_method_raises(rows):
    with pytest.raises(AnonymizerError, match="Unknown method"):
        anonymize(rows, ["name"], method="rot13")


def test_empty_rows_returns_empty_result():
    result = anonymize([], ["email"])
    assert result.rows == []
    assert result.row_count == 0


def test_multiple_columns_anonymized(rows):
    result = anonymize(rows, ["name", "email"])
    assert result.rows[0]["name"] != "Alice"
    assert result.rows[0]["email"] != "alice@example.com"
    assert result.anonymized_columns == ["name", "email"]


def test_hash_value_length():
    assert len(_hash_value("test")) == 16


def test_mask_value_full():
    assert _mask_value("hello") == "*****"
