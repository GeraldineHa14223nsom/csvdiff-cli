"""Tests for csvdiff.unpivotter and csvdiff.cli_unpivot."""
import csv
import io
import pytest
from csvdiff.unpivotter import unpivot, UnpivotError, unpivoted_row_count


ROWS = [
    {"id": "1", "name": "alice", "jan": "10", "feb": "20"},
    {"id": "2", "name": "bob",   "jan": "30", "feb": "40"},
]


def test_unpivot_row_count():
    result = unpivot(ROWS, id_columns=["id", "name"], value_columns=["jan", "feb"])
    assert unpivoted_row_count(result) == 4  # 2 rows * 2 value cols


def test_unpivot_headers():
    result = unpivot(ROWS, id_columns=["id"], value_columns=["jan", "feb"])
    assert result.headers == ["id", "variable", "value"]


def test_unpivot_custom_names():
    result = unpivot(ROWS, id_columns=["id"], value_columns=["jan"],
                     var_name="month", value_name="amount")
    assert "month" in result.headers
    assert "amount" in result.headers


def test_unpivot_values_correct():
    result = unpivot(ROWS, id_columns=["id", "name"], value_columns=["jan", "feb"])
    first = result.rows[0]
    assert first["id"] == "1"
    assert first["variable"] == "jan"
    assert first["value"] == "10"


def test_unpivot_preserves_id_values():
    result = unpivot(ROWS, id_columns=["id", "name"], value_columns=["jan"])
    ids = [r["id"] for r in result.rows]
    assert ids == ["1", "2"]


def test_unpivot_empty_rows():
    result = unpivot([], id_columns=["id"], value_columns=["jan"])
    assert result.rows == []
    assert result.original_row_count == 0


def test_unpivot_unknown_id_column_raises():
    with pytest.raises(UnpivotError, match="id column"):
        unpivot(ROWS, id_columns=["missing"], value_columns=["jan"])


def test_unpivot_unknown_value_column_raises():
    with pytest.raises(UnpivotError, match="value column"):
        unpivot(ROWS, id_columns=["id"], value_columns=["missing"])


def test_unpivot_no_value_columns_raises():
    with pytest.raises(UnpivotError, match="at least one"):
        unpivot(ROWS, id_columns=["id"], value_columns=[])


def test_unpivot_original_row_count():
    result = unpivot(ROWS, id_columns=["id"], value_columns=["jan", "feb"])
    assert result.original_row_count == 2


def test_unpivot_value_columns_stored():
    result = unpivot(ROWS, id_columns=["id"], value_columns=["jan", "feb"])
    assert result.value_columns == ["jan", "feb"]


# CLI smoke test
def test_cmd_unpivot_exits_zero(tmp_path):
    from csvdiff.cli_unpivot import cmd_unpivot
    import argparse
    f = tmp_path / "data.csv"
    f.write_text("id,jan,feb\n1,10,20\n2,30,40\n")

    args = argparse.Namespace(
        file=str(f),
        id_columns="id",
        value_columns="jan,feb",
        var_name="variable",
        value_name="value",
        output=None,
    )
    assert cmd_unpivot(args) == 0


def test_cmd_unpivot_missing_file_returns_2(tmp_path):
    from csvdiff.cli_unpivot import cmd_unpivot
    import argparse
    args = argparse.Namespace(
        file=str(tmp_path / "nope.csv"),
        id_columns="id",
        value_columns="jan",
        var_name="variable",
        value_name="value",
        output=None,
    )
    assert cmd_unpivot(args) == 2
