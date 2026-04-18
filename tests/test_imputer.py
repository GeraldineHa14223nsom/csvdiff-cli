import pytest
from csvdiff.imputer import impute, ImputerError, ImputeResult

HEADERS = ["id", "name", "score"]


def _rows():
    return [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "", "score": ""},
        {"id": "3", "name": "Bob", "score": ""},
    ]


def test_returns_impute_result():
    r = impute(HEADERS, _rows(), fill_value="N/A")
    assert isinstance(r, ImputeResult)


def test_fill_all_empty_with_default():
    r = impute(HEADERS, _rows(), fill_value="N/A")
    assert r.rows[1]["name"] == "N/A"
    assert r.rows[1]["score"] == "N/A"


def test_non_empty_values_unchanged():
    r = impute(HEADERS, _rows(), fill_value="N/A")
    assert r.rows[0]["name"] == "Alice"
    assert r.rows[0]["score"] == "90"


def test_filled_count():
    r = impute(HEADERS, _rows(), fill_value="N/A")
    assert r.filled_count == 3


def test_column_counts():
    r = impute(HEADERS, _rows(), fill_value="N/A")
    assert r.column_counts["name"] == 1
    assert r.column_counts["score"] == 2


def test_fill_map_per_column():
    r = impute(HEADERS, _rows(), fill_map={"score": "0", "name": "Unknown"})
    assert r.rows[1]["score"] == "0"
    assert r.rows[1]["name"] == "Unknown"


def test_fill_map_takes_precedence_over_fill_value():
    r = impute(HEADERS, _rows(), fill_map={"score": "0"}, fill_value="N/A")
    assert r.rows[1]["score"] == "0"
    assert r.rows[1]["name"] == "N/A"


def test_restrict_to_columns():
    r = impute(HEADERS, _rows(), fill_value="?", columns=["name"])
    assert r.rows[1]["name"] == "?"
    assert r.rows[1]["score"] == ""  # untouched


def test_unknown_column_in_fill_map_raises():
    with pytest.raises(ImputerError, match="Unknown columns"):
        impute(HEADERS, _rows(), fill_map={"nonexistent": "x"})


def test_empty_rows_returns_zero_filled():
    r = impute(HEADERS, [], fill_value="N/A")
    assert r.filled_count == 0
    assert r.rows == []


def test_headers_preserved():
    r = impute(HEADERS, _rows(), fill_value="x")
    assert r.headers == HEADERS
