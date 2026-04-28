"""Tests for csvdiff.spliceor."""
import pytest
from csvdiff.spliceor import splice, SplicerError, SpliceResult


@pytest.fixture()
def base_rows():
    return [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Carol"},
    ]


@pytest.fixture()
def new_rows():
    return [{"id": "99", "name": "Zara"}]


def test_returns_splice_result(base_rows, new_rows):
    result = splice(base_rows, new_rows, position=1)
    assert isinstance(result, SpliceResult)


def test_total_count_is_sum(base_rows, new_rows):
    result = splice(base_rows, new_rows, position=1)
    assert result.total_count == len(base_rows) + len(new_rows)


def test_original_count_preserved(base_rows, new_rows):
    result = splice(base_rows, new_rows, position=0)
    assert result.original_count == 3


def test_inserted_count_correct(base_rows, new_rows):
    result = splice(base_rows, new_rows, position=0)
    assert result.inserted_count == 1


def test_position_stored(base_rows, new_rows):
    result = splice(base_rows, new_rows, position=2)
    assert result.position == 2


def test_insert_at_start_prepends(base_rows, new_rows):
    result = splice(base_rows, new_rows, position=0)
    assert result.rows[0]["id"] == "99"


def test_insert_at_end_appends(base_rows, new_rows):
    result = splice(base_rows, new_rows, position=3)
    assert result.rows[-1]["id"] == "99"


def test_insert_in_middle(base_rows, new_rows):
    result = splice(base_rows, new_rows, position=1)
    assert result.rows[1]["id"] == "99"
    assert result.rows[0]["id"] == "1"
    assert result.rows[2]["id"] == "2"


def test_missing_key_filled_with_default(base_rows):
    partial = [{"id": "10"}]  # no 'name' key
    result = splice(base_rows, partial, position=1, fill_value="N/A")
    assert result.rows[1]["name"] == "N/A"


def test_extra_key_in_insert_ignored(base_rows):
    extra = [{"id": "10", "name": "Dave", "extra": "ignored"}]
    result = splice(base_rows, extra, position=0)
    assert "extra" not in result.rows[0]


def test_negative_position_raises(base_rows, new_rows):
    with pytest.raises(SplicerError, match="position must be"):
        splice(base_rows, new_rows, position=-1)


def test_position_beyond_length_raises(base_rows, new_rows):
    with pytest.raises(SplicerError, match="exceeds row count"):
        splice(base_rows, new_rows, position=99)


def test_empty_insert_raises(base_rows):
    with pytest.raises(SplicerError, match="must not be empty"):
        splice(base_rows, [], position=0)


def test_headers_match_base(base_rows, new_rows):
    result = splice(base_rows, new_rows, position=0)
    assert result.headers == ["id", "name"]
