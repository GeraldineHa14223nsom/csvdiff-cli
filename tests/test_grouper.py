"""Unit tests for csvdiff.grouper."""
import pytest

from csvdiff.grouper import GrouperError, GroupResult, group_rows

ROWS = [
    {"dept": "eng", "name": "Alice", "salary": "90000"},
    {"dept": "eng", "name": "Bob",   "salary": "85000"},
    {"dept": "hr",  "name": "Carol", "salary": "70000"},
    {"dept": "hr",  "name": "Dave",  "salary": "72000"},
    {"dept": "eng", "name": "Eve",   "salary": "95000"},
]


def test_group_count():
    result = group_rows(ROWS, ["dept"])
    assert result.group_count() == 2


def test_row_count():
    result = group_rows(ROWS, ["dept"])
    assert result.row_count() == 5


def test_group_sizes():
    result = group_rows(ROWS, ["dept"])
    assert len(result.groups[("eng",)]) == 3
    assert len(result.groups[("hr",)]) == 2


def test_group_keys_stored():
    result = group_rows(ROWS, ["dept"])
    assert result.group_keys == ["dept"]


def test_multi_key_grouping():
    rows = [
        {"dept": "eng", "level": "senior", "name": "Alice"},
        {"dept": "eng", "level": "junior", "name": "Bob"},
        {"dept": "eng", "level": "senior", "name": "Eve"},
    ]
    result = group_rows(rows, ["dept", "level"])
    assert result.group_count() == 2
    assert len(result.groups[("eng", "senior")]) == 2


def test_empty_rows_returns_empty_groups():
    result = group_rows([], ["dept"])
    assert result.group_count() == 0
    assert result.row_count() == 0


def test_no_keys_raises():
    with pytest.raises(GrouperError, match="At least one group key"):
        group_rows(ROWS, [])


def test_unknown_key_raises():
    with pytest.raises(GrouperError, match="not found in data"):
        group_rows(ROWS, ["nonexistent"])


def test_to_summary_rows_total():
    result = group_rows(ROWS, ["dept"])
    summary = result.to_summary_rows("salary", "total")
    totals = {r["dept"]: float(r["total_salary"]) for r in summary}
    assert totals["eng"] == pytest.approx(270000.0)
    assert totals["hr"] == pytest.approx(142000.0)


def test_to_summary_rows_count():
    result = group_rows(ROWS, ["dept"])
    summary = result.to_summary_rows("salary", "count")
    counts = {r["dept"]: float(r["count_salary"]) for r in summary}
    assert counts["eng"] == 3
    assert counts["hr"] == 2
