import pytest
from csvdiff.binner import bin_column, BinnerError


@pytest.fixture
def rows():
    return [
        {"id": "1", "score": "15"},
        {"id": "2", "score": "45"},
        {"id": "3", "score": "75"},
        {"id": "4", "score": "95"},
        {"id": "5", "score": "200"},
    ]


def test_bin_result_has_new_column(rows):
    result = bin_column(rows, "score", [0, 50, 100])
    assert all("score_bin" in r for r in result.rows)


def test_bin_assigns_correct_labels(rows):
    result = bin_column(rows, "score", [0, 50, 100])
    labels = [r["score_bin"] for r in result.rows]
    assert labels[0] == "0-50"
    assert labels[1] == "0-50"
    assert labels[2] == "50-100"
    assert labels[3] == "50-100"


def test_bin_out_of_range(rows):
    result = bin_column(rows, "score", [0, 50, 100])
    assert result.rows[4]["score_bin"] == "other"


def test_custom_labels(rows):
    result = bin_column(rows, "score", [0, 50, 100], labels=["low", "high"])
    assert result.rows[0]["score_bin"] == "low"
    assert result.rows[2]["score_bin"] == "high"


def test_custom_bin_column_name(rows):
    result = bin_column(rows, "score", [0, 50, 100], bin_column="bucket")
    assert "bucket" in result.rows[0]
    assert result.bin_column == "bucket"


def test_bin_counts_sum_to_total(rows):
    result = bin_column(rows, "score", [0, 50, 100])
    total = sum(result.bin_counts.values())
    assert total == len(rows)


def test_bin_counts_correct(rows):
    result = bin_column(rows, "score", [0, 50, 100])
    assert result.bin_counts["0-50"] == 2
    assert result.bin_counts["50-100"] == 2
    assert result.bin_counts["other"] == 1


def test_unknown_column_raises(rows):
    with pytest.raises(BinnerError, match="not found"):
        bin_column(rows, "missing", [0, 50, 100])


def test_too_few_boundaries_raises(rows):
    with pytest.raises(BinnerError, match="two boundary"):
        bin_column(rows, "score", [50])


def test_wrong_label_count_raises(rows):
    with pytest.raises(BinnerError, match="labels"):
        bin_column(rows, "score", [0, 50, 100], labels=["only_one"])


def test_empty_rows_returns_empty_result():
    result = bin_column([], "score", [0, 50, 100])
    assert result.rows == []


def test_headers_include_bin_column(rows):
    result = bin_column(rows, "score", [0, 50, 100])
    assert "score_bin" in result.headers
