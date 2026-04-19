import pytest
from csvdiff.ranker import rank_rows, RankResult, RankerError


@pytest.fixture
def rows():
    return [
        {"name": "alice", "score": "30"},
        {"name": "bob",   "score": "10"},
        {"name": "carol", "score": "20"},
        {"name": "dave",  "score": "10"},
    ]


def test_returns_rank_result(rows):
    result = rank_rows(rows, "score")
    assert isinstance(result, RankResult)


def test_ranked_count(rows):
    result = rank_rows(rows, "score")
    assert result.ranked_count == 4


def test_rank_column_added(rows):
    result = rank_rows(rows, "score")
    assert "rank" in result.rows[0]


def test_custom_rank_column(rows):
    result = rank_rows(rows, "score", rank_column="pos")
    assert "pos" in result.rows[0]


def test_ascending_order(rows):
    result = rank_rows(rows, "score", ascending=True)
    ranks = {r["name"]: int(r["rank"]) for r in result.rows}
    assert ranks["bob"] < ranks["carol"] < ranks["alice"]


def test_descending_order(rows):
    result = rank_rows(rows, "score", ascending=False)
    ranks = {r["name"]: int(r["rank"]) for r in result.rows}
    assert ranks["alice"] < ranks["carol"] < ranks["bob"]


def test_dense_ties_share_rank(rows):
    result = rank_rows(rows, "score", ascending=True, method="dense")
    ranks = {r["name"]: int(r["rank"]) for r in result.rows}
    assert ranks["bob"] == ranks["dave"]


def test_standard_ties_same_position(rows):
    result = rank_rows(rows, "score", ascending=True, method="standard")
    ranks = {r["name"]: int(r["rank"]) for r in result.rows}
    assert ranks["bob"] == ranks["dave"]


def test_unknown_column_raises(rows):
    with pytest.raises(RankerError, match="not found"):
        rank_rows(rows, "missing")


def test_non_numeric_raises(rows):
    bad = [{"score": "abc"}]
    with pytest.raises(RankerError, match="Non-numeric"):
        rank_rows(bad, "score")


def test_unknown_method_raises(rows):
    with pytest.raises(RankerError, match="Unknown rank method"):
        rank_rows(rows, "score", method="fractional")


def test_empty_rows_returns_empty():
    result = rank_rows([], "score")
    assert result.rows == []
    assert result.ranked_count == 0


def test_original_columns_preserved(rows):
    result = rank_rows(rows, "score")
    assert all("name" in r and "score" in r for r in result.rows)
