"""Tests for csvdiff.masker."""
import pytest
from csvdiff.masker import mask, MaskerError, MaskResult


@pytest.fixture
def rows():
    return [
        {"id": "1", "name": "Alice", "email": "alice@example.com", "score": "95"},
        {"id": "2", "name": "Bob",   "email": "bob@example.com",   "score": "80"},
        {"id": "3", "name": "Carol", "email": "carol@example.com", "score": "70"},
    ]


def test_returns_mask_result(rows):
    result = mask(rows, ["email"])
    assert isinstance(result, MaskResult)


def test_row_count_unchanged(rows):
    result = mask(rows, ["email"])
    assert result.row_count == 3


def test_masked_columns_recorded(rows):
    result = mask(rows, ["email", "name"])
    assert sorted(result.masked_columns) == ["email", "name"]


def test_masked_count_equals_rows_times_columns(rows):
    result = mask(rows, ["email", "name"])
    assert result.masked_count == 6  # 3 rows × 2 columns


def test_default_mask_replaces_with_stars(rows):
    result = mask(rows, ["email"])
    for row in result.rows:
        assert row["email"] == "******"


def test_custom_mask_char(rows):
    result = mask(rows, ["name"], mask_char="#", mask_length=4)
    for row in result.rows:
        assert row["name"] == "####"


def test_custom_mask_length(rows):
    result = mask(rows, ["email"], mask_length=3)
    for row in result.rows:
        assert row["email"] == "***"


def test_unmasked_columns_preserved(rows):
    result = mask(rows, ["email"])
    assert result.rows[0]["name"] == "Alice"
    assert result.rows[1]["score"] == "80"


def test_partial_mode_keeps_leading_chars(rows):
    result = mask(rows, ["name"], partial=True, visible_chars=2)
    assert result.rows[0]["name"] == "Al***"
    assert result.rows[1]["name"] == "Bo*"


def test_partial_mode_custom_visible_chars(rows):
    result = mask(rows, ["email"], partial=True, visible_chars=3)
    for row in result.rows:
        assert row["email"][:3] in ("ali", "bob", "car")
        assert "*" in row["email"]


def test_headers_preserved(rows):
    result = mask(rows, ["email"])
    assert result.headers == ["id", "name", "email", "score"]


def test_empty_rows_returns_empty_result():
    result = mask([], ["email"])
    assert result.row_count == 0
    assert result.masked_count == 0
    assert result.headers == []


def test_unknown_column_raises(rows):
    with pytest.raises(MaskerError, match="not found"):
        mask(rows, ["nonexistent"])


def test_multiple_unknown_columns_raises(rows):
    with pytest.raises(MaskerError):
        mask(rows, ["foo", "bar"])


def test_empty_value_not_counted(rows):
    sparse = [{"id": "1", "name": "", "email": "a@b.com"}]
    result = mask(sparse, ["name", "email"])
    # 'name' is empty so only 'email' is counted
    assert result.masked_count == 1
