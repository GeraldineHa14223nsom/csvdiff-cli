"""Tests for csvdiff.condenser."""
import pytest

from csvdiff.condenser import CondenseResult, CondenserError, condense


@pytest.fixture
def rows():
    return [
        {"id": "1", "name": "Alice", "tag": "python"},
        {"id": "1", "name": "Alice", "tag": "data"},
        {"id": "2", "name": "Bob",   "tag": "java"},
        {"id": "2", "name": "Bob",   "tag": "spring"},
        {"id": "2", "name": "Bob",   "tag": "rest"},
        {"id": "3", "name": "Carol", "tag": "go"},
    ]


def test_returns_condense_result(rows):
    result = condense(rows, key_columns=["id"], agg_column="tag")
    assert isinstance(result, CondenseResult)


def test_condensed_count(rows):
    result = condense(rows, key_columns=["id"], agg_column="tag")
    assert result.condensed_count == 3


def test_original_count(rows):
    result = condense(rows, key_columns=["id"], agg_column="tag")
    assert result.original_count == 6


def test_reduction_count(rows):
    result = condense(rows, key_columns=["id"], agg_column="tag")
    assert result.reduction_count == 3


def test_reduction_rate(rows):
    result = condense(rows, key_columns=["id"], agg_column="tag")
    assert abs(result.reduction_rate - 0.5) < 1e-9


def test_values_joined_with_separator(rows):
    result = condense(rows, key_columns=["id"], agg_column="tag")
    row_map = {r["id"]: r for r in result.rows}
    assert row_map["1"]["tag"] == "python|data"
    assert row_map["2"]["tag"] == "java|spring|rest"
    assert row_map["3"]["tag"] == "go"


def test_custom_separator(rows):
    result = condense(rows, key_columns=["id"], agg_column="tag", separator=",")
    row_map = {r["id"]: r for r in result.rows}
    assert row_map["2"]["tag"] == "java,spring,rest"


def test_other_columns_preserved(rows):
    result = condense(rows, key_columns=["id"], agg_column="tag")
    row_map = {r["id"]: r for r in result.rows}
    assert row_map["1"]["name"] == "Alice"
    assert row_map["2"]["name"] == "Bob"


def test_headers_preserved(rows):
    result = condense(rows, key_columns=["id"], agg_column="tag")
    assert result.headers == ["id", "name", "tag"]


def test_empty_rows_returns_empty_result():
    result = condense([], key_columns=["id"], agg_column="tag")
    assert result.rows == []
    assert result.original_count == 0
    assert result.condensed_count == 0
    assert result.reduction_rate == 0.0


def test_unknown_key_column_raises(rows):
    with pytest.raises(CondenserError, match="Key column 'missing'"):
        condense(rows, key_columns=["missing"], agg_column="tag")


def test_unknown_agg_column_raises(rows):
    with pytest.raises(CondenserError, match="Aggregate column 'nope'"):
        condense(rows, key_columns=["id"], agg_column="nope")


def test_agg_column_same_as_key_raises(rows):
    with pytest.raises(CondenserError, match="cannot also be a key column"):
        condense(rows, key_columns=["tag"], agg_column="tag")


def test_multi_key_grouping():
    data = [
        {"dept": "eng", "team": "backend", "skill": "python"},
        {"dept": "eng", "team": "backend", "skill": "sql"},
        {"dept": "eng", "team": "frontend", "skill": "js"},
    ]
    result = condense(data, key_columns=["dept", "team"], agg_column="skill")
    assert result.condensed_count == 2
    rows_by_team = {r["team"]: r for r in result.rows}
    assert rows_by_team["backend"]["skill"] == "python|sql"
    assert rows_by_team["frontend"]["skill"] == "js"
