"""Tests for csvdiff.sequencer."""
import pytest
from csvdiff.sequencer import SequencerError, SequenceResult, sequence_rows


@pytest.fixture
def rows():
    return [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Carol"},
    ]


def test_returns_sequence_result(rows):
    result = sequence_rows(rows)
    assert isinstance(result, SequenceResult)


def test_row_count_unchanged(rows):
    result = sequence_rows(rows)
    assert result.row_count == 3
    assert result.original_count == 3


def test_seq_column_added(rows):
    result = sequence_rows(rows)
    assert "seq" in result.rows[0]


def test_default_start_is_one(rows):
    result = sequence_rows(rows)
    assert result.rows[0]["seq"] == "1"


def test_default_step_is_one(rows):
    result = sequence_rows(rows)
    values = [int(r["seq"]) for r in result.rows]
    assert values == [1, 2, 3]


def test_custom_start(rows):
    result = sequence_rows(rows, start=10)
    assert result.rows[0]["seq"] == "10"


def test_custom_step(rows):
    result = sequence_rows(rows, step=5)
    values = [int(r["seq"]) for r in result.rows]
    assert values == [1, 6, 11]


def test_negative_step(rows):
    result = sequence_rows(rows, start=100, step=-10)
    values = [int(r["seq"]) for r in result.rows]
    assert values == [100, 90, 80]


def test_custom_column_name(rows):
    result = sequence_rows(rows, column="row_num")
    assert "row_num" in result.rows[0]
    assert "seq" not in result.rows[0]


def test_seq_column_is_first(rows):
    result = sequence_rows(rows)
    assert list(result.rows[0].keys())[0] == "seq"


def test_original_values_preserved(rows):
    result = sequence_rows(rows)
    assert result.rows[1]["name"] == "Bob"


def test_empty_rows():
    result = sequence_rows([])
    assert result.rows == []
    assert result.row_count == 0


def test_zero_step_raises(rows):
    with pytest.raises(SequencerError, match="step"):
        sequence_rows(rows, step=0)


def test_empty_column_raises(rows):
    with pytest.raises(SequencerError, match="column"):
        sequence_rows(rows, column="")


def test_existing_column_raises(rows):
    with pytest.raises(SequencerError, match="already exists"):
        sequence_rows(rows, column="id")


def test_overwrite_allows_existing_column(rows):
    result = sequence_rows(rows, column="id", overwrite=True)
    assert result.rows[0]["id"] == "1"
