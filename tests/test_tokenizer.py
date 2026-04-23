"""Tests for csvdiff.tokenizer."""
import pytest
from csvdiff.tokenizer import TokenResult, TokenizerError, tokenize


@pytest.fixture()
def rows():
    return [
        {"id": "1", "tags": "alpha beta gamma"},
        {"id": "2", "tags": "alpha delta"},
        {"id": "3", "tags": "beta"},
        {"id": "4", "tags": ""},
    ]


def test_returns_token_result(rows):
    result = tokenize(rows, "tags")
    assert isinstance(result, TokenResult)


def test_total_rows(rows):
    result = tokenize(rows, "tags")
    assert result.total_rows == 4


def test_vocabulary_size(rows):
    result = tokenize(rows, "tags")
    # alpha, beta, gamma, delta
    assert result.vocabulary_size == 4


def test_token_counts_correct(rows):
    result = tokenize(rows, "tags")
    assert result.token_counts["alpha"] == 2
    assert result.token_counts["beta"] == 2
    assert result.token_counts["gamma"] == 1
    assert result.token_counts["delta"] == 1


def test_top_n_returns_most_common(rows):
    result = tokenize(rows, "tags")
    top = result.top_n(2)
    assert len(top) == 2
    tokens = [t for t, _ in top]
    assert "alpha" in tokens
    assert "beta" in tokens


def test_frequency_known_token(rows):
    result = tokenize(rows, "tags")
    assert result.frequency("alpha") == pytest.approx(0.5)


def test_frequency_unknown_token(rows):
    result = tokenize(rows, "tags")
    assert result.frequency("zzz") == 0.0


def test_tokens_are_lowercased():
    rows = [{"text": "Hello WORLD hello"}]
    result = tokenize(rows, "text")
    assert result.token_counts.get("hello") == 2
    assert result.token_counts.get("world") == 1


def test_min_length_filters_short_tokens():
    rows = [{"text": "a bb ccc dddd"}]
    result = tokenize(rows, "text", min_length=3)
    assert "a" not in result.token_counts
    assert "bb" not in result.token_counts
    assert "ccc" in result.token_counts
    assert "dddd" in result.token_counts


def test_custom_split_pattern():
    rows = [{"csv": "one,two,three"}]
    result = tokenize(rows, "csv", split_pattern=r",")
    assert result.vocabulary_size == 3


def test_empty_rows_raises():
    with pytest.raises(TokenizerError, match="empty"):
        tokenize([], "col")


def test_missing_column_raises():
    rows = [{"a": "1"}]
    with pytest.raises(TokenizerError, match="column 'z' not found"):
        tokenize(rows, "z")


def test_invalid_min_length_raises():
    rows = [{"text": "hello"}]
    with pytest.raises(TokenizerError, match="min_length"):
        tokenize(rows, "text", min_length=0)


def test_empty_cell_produces_no_tokens():
    rows = [{"text": ""}]
    result = tokenize(rows, "text")
    assert result.vocabulary_size == 0
    assert result.total_rows == 1
