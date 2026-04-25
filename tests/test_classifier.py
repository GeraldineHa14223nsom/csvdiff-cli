"""Tests for csvdiff.classifier."""
import pytest
from csvdiff.classifier import classify, ClassifierError, ClassifyResult


@pytest.fixture
def rows():
    return [
        {"name": "Alice", "score": "92"},
        {"name": "Bob", "score": "45"},
        {"name": "Carol", "score": "73"},
        {"name": "Dave", "score": "10"},
    ]


PATTERN_RULES = [
    {"label": "alice_group", "pattern": r"^alice$"},
    {"label": "other", "pattern": r".*"},
]

RANGE_RULES = [
    {"label": "high", "range": [80, 100]},
    {"label": "mid", "range": [50, 79]},
    {"label": "low", "range": [0, 49]},
]


def test_returns_classify_result(rows):
    result = classify(rows, "name", PATTERN_RULES)
    assert isinstance(result, ClassifyResult)


def test_label_column_added(rows):
    result = classify(rows, "name", PATTERN_RULES)
    assert all("label" in r for r in result.rows)


def test_custom_label_column(rows):
    result = classify(rows, "name", PATTERN_RULES, label_column="category")
    assert all("category" in r for r in result.rows)


def test_pattern_rule_matches_alice(rows):
    result = classify(rows, "name", PATTERN_RULES)
    alice_row = next(r for r in result.rows if r["name"] == "Alice")
    assert alice_row["label"] == "alice_group"


def test_range_rule_high(rows):
    result = classify(rows, "score", RANGE_RULES)
    alice_row = next(r for r in result.rows if r["name"] == "Alice")
    assert alice_row["label"] == "high"


def test_range_rule_low(rows):
    result = classify(rows, "score", RANGE_RULES)
    dave_row = next(r for r in result.rows if r["name"] == "Dave")
    assert dave_row["label"] == "low"


def test_classified_count(rows):
    result = classify(rows, "score", RANGE_RULES)
    assert result.classified_count == 4


def test_unmatched_count_with_default(rows):
    rules = [{"label": "high", "range": [90, 100]}]
    result = classify(rows, "score", rules, default_label="unknown")
    assert result.unmatched_count == 3


def test_default_label_applied(rows):
    rules = [{"label": "high", "range": [90, 100]}]
    result = classify(rows, "score", rules, default_label="other")
    bob_row = next(r for r in result.rows if r["name"] == "Bob")
    assert bob_row["label"] == "other"


def test_row_count_preserved(rows):
    result = classify(rows, "name", PATTERN_RULES)
    assert len(result.rows) == len(rows)


def test_no_rules_raises(rows):
    with pytest.raises(ClassifierError):
        classify(rows, "name", [])


def test_missing_column_raises(rows):
    with pytest.raises(ClassifierError):
        classify(rows, "nonexistent", PATTERN_RULES)


def test_rule_without_label_raises(rows):
    with pytest.raises(ClassifierError):
        classify(rows, "name", [{"pattern": ".*"}])


def test_rule_without_pattern_or_range_raises(rows):
    with pytest.raises(ClassifierError):
        classify(rows, "name", [{"label": "x"}])


def test_empty_rows_returns_empty_result():
    result = classify([], "score", RANGE_RULES)
    assert result.rows == []
    assert result.classified_count == 0
