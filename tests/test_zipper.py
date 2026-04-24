"""Tests for csvdiff.zipper."""
import pytest
from csvdiff.zipper import zip_rows, ZipResult, ZipperError


LEFT = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "3", "name": "Carol"},
]

RIGHT = [
    {"score": "90", "grade": "A"},
    {"score": "75", "grade": "B"},
    {"score": "82", "grade": "B+"},
]


def test_returns_zip_result():
    result = zip_rows(LEFT, RIGHT)
    assert isinstance(result, ZipResult)


def test_row_count_equals_longer_side():
    result = zip_rows(LEFT, RIGHT)
    assert result.row_count == 3


def test_column_count_is_sum_of_both_sides():
    result = zip_rows(LEFT, RIGHT)
    assert result.column_count == 4  # id, name, score, grade


def test_headers_contain_all_columns():
    result = zip_rows(LEFT, RIGHT)
    assert result.headers == ["id", "name", "score", "grade"]


def test_values_merged_correctly():
    result = zip_rows(LEFT, RIGHT)
    assert result.rows[0] == {"id": "1", "name": "Alice", "score": "90", "grade": "A"}
    assert result.rows[1] == {"id": "2", "name": "Bob", "score": "75", "grade": "B"}


def test_left_row_count_stored():
    result = zip_rows(LEFT, RIGHT)
    assert result.left_row_count == 3


def test_right_row_count_stored():
    result = zip_rows(LEFT, RIGHT)
    assert result.right_row_count == 3


def test_shorter_right_fills_with_empty():
    short_right = RIGHT[:2]
    result = zip_rows(LEFT, short_right, fill="")
    assert result.rows[2]["score"] == ""
    assert result.rows[2]["grade"] == ""


def test_shorter_left_fills_with_empty():
    short_left = LEFT[:1]
    result = zip_rows(short_left, RIGHT, fill="N/A")
    assert result.rows[1]["id"] == "N/A"
    assert result.rows[2]["name"] == "N/A"


def test_prefix_applied_to_left_columns():
    result = zip_rows(LEFT, RIGHT, left_prefix="l_", right_prefix="r_")
    assert "l_id" in result.headers
    assert "l_name" in result.headers


def test_prefix_applied_to_right_columns():
    result = zip_rows(LEFT, RIGHT, left_prefix="l_", right_prefix="r_")
    assert "r_score" in result.headers
    assert "r_grade" in result.headers


def test_prefix_values_accessible_in_rows():
    result = zip_rows(LEFT, RIGHT, left_prefix="l_", right_prefix="r_")
    assert result.rows[0]["l_name"] == "Alice"
    assert result.rows[0]["r_score"] == "90"


def test_column_collision_without_prefix_raises():
    overlapping = [{"name": "X", "score": "1"}]
    left_with_overlap = [{"name": "Alice", "score": "99"}]
    with pytest.raises(ZipperError, match="collision"):
        zip_rows(left_with_overlap, overlapping)


def test_empty_left_raises():
    with pytest.raises(ZipperError):
        zip_rows([], RIGHT)


def test_empty_right_raises():
    with pytest.raises(ZipperError):
        zip_rows(LEFT, [])
