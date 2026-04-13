"""Unit tests for csvdiff.joiner."""
import pytest

from csvdiff.joiner import JoinError, JoinResult, join

LEFT = [
    {"id": "1", "name": "Alice", "dept": "Eng"},
    {"id": "2", "name": "Bob", "dept": "HR"},
    {"id": "3", "name": "Carol", "dept": "Eng"},
]

RIGHT = [
    {"id": "1", "salary": "90000"},
    {"id": "2", "salary": "70000"},
    {"id": "4", "salary": "80000"},
]


def test_inner_join_returns_matching_rows():
    result = join(LEFT, RIGHT, key="id", how="inner")
    assert len(result.rows) == 2
    ids = {r["id"] for r in result.rows}
    assert ids == {"1", "2"}


def test_inner_join_merges_columns():
    result = join(LEFT, RIGHT, key="id", how="inner")
    row = next(r for r in result.rows if r["id"] == "1")
    assert row["name"] == "Alice"
    assert row["salary"] == "90000"


def test_left_join_includes_left_only():
    result = join(LEFT, RIGHT, key="id", how="left")
    assert len(result.rows) == 2
    assert len(result.left_only) == 1
    assert result.left_only[0]["id"] == "3"


def test_right_join_includes_right_only():
    result = join(LEFT, RIGHT, key="id", how="right")
    assert len(result.rows) == 2
    assert len(result.right_only) == 1
    assert result.right_only[0]["id"] == "4"


def test_outer_join_includes_both_sides():
    result = join(LEFT, RIGHT, key="id", how="outer")
    assert len(result.rows) == 2
    assert len(result.left_only) == 1
    assert len(result.right_only) == 1


def test_conflicting_columns_get_suffixed():
    left = [{"id": "1", "value": "a"}]
    right = [{"id": "1", "value": "b"}]
    result = join(left, right, key="id", how="inner")
    row = result.rows[0]
    assert "value_left" in row
    assert "value_right" in row
    assert row["value_left"] == "a"
    assert row["value_right"] == "b"


def test_unknown_join_type_raises():
    with pytest.raises(JoinError, match="Unknown join type"):
        join(LEFT, RIGHT, key="id", how="cross")


def test_missing_key_column_raises():
    with pytest.raises(JoinError, match="Key column"):
        join(LEFT, RIGHT, key="missing", how="inner")


def test_empty_left_returns_empty_inner():
    result = join([], RIGHT, key="id", how="inner")
    assert result.rows == []


def test_join_result_stores_join_type():
    result = join(LEFT, RIGHT, key="id", how="left")
    assert result.join_type == "left"
