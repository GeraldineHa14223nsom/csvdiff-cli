import pytest
from csvdiff.reshaper import reshape, ReshapeResult, ReshaperError


@pytest.fixture
def rows():
    return [
        {"id": "1", "name": "Alice", "age": "30"},
        {"id": "2", "name": "Bob", "age": "25"},
    ]


def test_returns_reshape_result(rows):
    result = reshape(rows, ["id", "name", "age"])
    assert isinstance(result, ReshapeResult)


def test_reorder_columns(rows):
    result = reshape(rows, ["age", "id", "name"])
    assert result.headers == ["age", "id", "name"]
    assert list(result.rows[0].keys()) == ["age", "id", "name"]


def test_drop_extra_column(rows):
    result = reshape(rows, ["id", "name"])
    assert "age" not in result.rows[0]
    assert result.dropped_columns == ["age"]


def test_add_missing_column(rows):
    result = reshape(rows, ["id", "name", "age", "email"])
    assert result.rows[0]["email"] == ""
    assert "email" in result.added_columns


def test_fill_value_respected(rows):
    result = reshape(rows, ["id", "name", "score"], fill_value="N/A")
    assert result.rows[0]["score"] == "N/A"


def test_row_count(rows):
    result = reshape(rows, ["id", "name"])
    assert result.row_count == 2


def test_empty_rows():
    result = reshape([], ["id", "name"])
    assert result.row_count == 0
    assert result.headers == ["id", "name"]
    assert result.added_columns == ["id", "name"]
    assert result.dropped_columns == []


def test_empty_target_raises(rows):
    with pytest.raises(ReshaperError):
        reshape(rows, [])


def test_duplicate_target_raises(rows):
    with pytest.raises(ReshaperError):
        reshape(rows, ["id", "id", "name"])


def test_values_preserved(rows):
    result = reshape(rows, ["id", "name"])
    assert result.rows[0]["id"] == "1"
    assert result.rows[1]["name"] == "Bob"


def test_no_added_no_dropped(rows):
    result = reshape(rows, ["id", "name", "age"])
    assert result.added_columns == []
    assert result.dropped_columns == []
