"""Tests for csvdiff.fuzzer."""
import pytest

from csvdiff.fuzzer import (
    FuzzerError,
    FuzzyMatch,
    FuzzyResult,
    fuzzy_match,
)


@pytest.fixture()
def left_rows():
    return [
        {"id": "1", "name": "Alice Smith"},
        {"id": "2", "name": "Bob Jones"},
        {"id": "3", "name": "Charlie Brown"},
    ]


@pytest.fixture()
def right_rows():
    return [
        {"id": "A", "name": "Alice Smyth"},
        {"id": "B", "name": "Robert Jones"},
        {"id": "C", "name": "Xander White"},
    ]


def test_fuzzy_match_returns_fuzzy_result(left_rows, right_rows):
    result = fuzzy_match(left_rows, right_rows, key="name")
    assert isinstance(result, FuzzyResult)


def test_fuzzy_match_exact_names():
    left = [{"name": "Alice"}, {"name": "Bob"}]
    right = [{"name": "Alice"}, {"name": "Bob"}]
    result = fuzzy_match(left, right, key="name", threshold=1.0)
    assert result.match_count == 2
    assert result.unmatched_left == []
    assert result.unmatched_right == []


def test_fuzzy_match_alice_smyth(left_rows, right_rows):
    result = fuzzy_match(left_rows, right_rows, key="name", threshold=0.7)
    matched_left_keys = {m.left_key for m in result.matches}
    assert "Alice Smith" in matched_left_keys


def test_fuzzy_match_score_between_zero_and_one(left_rows, right_rows):
    result = fuzzy_match(left_rows, right_rows, key="name", threshold=0.5)
    for match in result.matches:
        assert 0.0 <= match.score <= 1.0


def test_fuzzy_match_unmatched_left_when_threshold_high(left_rows, right_rows):
    result = fuzzy_match(left_rows, right_rows, key="name", threshold=0.99)
    # No near-identical names, so most should be unmatched
    assert len(result.unmatched_left) > 0


def test_fuzzy_match_unmatched_right_preserved(left_rows, right_rows):
    result = fuzzy_match(left_rows, right_rows, key="name", threshold=0.7)
    # Xander White has no close match in left
    unmatched_names = [r["name"] for r in result.unmatched_right]
    assert "Xander White" in unmatched_names


def test_fuzzy_match_mean_score_none_when_no_matches():
    left = [{"name": "Alpha"}]
    right = [{"name": "Zeta"}]
    result = fuzzy_match(left, right, key="name", threshold=0.99)
    assert result.mean_score is None


def test_fuzzy_match_mean_score_float_when_matches():
    left = [{"name": "Alice"}]
    right = [{"name": "Alice"}]
    result = fuzzy_match(left, right, key="name", threshold=0.5)
    assert isinstance(result.mean_score, float)
    assert result.mean_score == pytest.approx(1.0)


def test_fuzzy_match_invalid_threshold_raises():
    with pytest.raises(FuzzerError, match="Threshold"):
        fuzzy_match([], [], key="name", threshold=1.5)


def test_fuzzy_match_missing_key_raises():
    left = [{"name": "Alice"}]
    right = [{"name": "Alice"}]
    with pytest.raises(FuzzerError, match="Key column"):
        fuzzy_match(left, right, key="email")


def test_fuzzy_match_empty_inputs():
    result = fuzzy_match([], [], key="name")
    assert result.match_count == 0
    assert result.unmatched_left == []
    assert result.unmatched_right == []


def test_fuzzy_match_left_empty():
    right = [{"name": "Alice"}]
    result = fuzzy_match([], right, key="name")
    assert result.match_count == 0
    assert result.unmatched_right == right
