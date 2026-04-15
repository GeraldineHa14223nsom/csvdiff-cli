"""Tests for csvdiff.transposer and csvdiff.cli_transpose."""
from __future__ import annotations

import csv
import io
import sys
import types
import pytest

from csvdiff.transposer import transpose, TransposeResult, TransposerError
from csvdiff.cli_transpose import cmd_transpose


HEADERS = ["id", "name", "score"]
ROWS = [
    {"id": "1", "name": "Alice", "score": "90"},
    {"id": "2", "name": "Bob", "score": "85"},
]


def test_transpose_returns_transpose_result():
    result = transpose(HEADERS, ROWS)
    assert isinstance(result, TransposeResult)


def test_transpose_original_counts():
    result = transpose(HEADERS, ROWS)
    assert result.original_row_count == 2
    assert result.original_col_count == 3


def test_transpose_new_headers():
    result = transpose(HEADERS, ROWS)
    assert result.headers == ["field", "row_0", "row_1"]


def test_transpose_row_count_equals_original_col_count():
    result = transpose(HEADERS, ROWS)
    assert len(result.rows) == len(HEADERS)


def test_transpose_field_column_contains_original_headers():
    result = transpose(HEADERS, ROWS)
    fields = [r["field"] for r in result.rows]
    assert fields == HEADERS


def test_transpose_values_correct():
    result = transpose(HEADERS, ROWS)
    name_row = next(r for r in result.rows if r["field"] == "name")
    assert name_row["row_0"] == "Alice"
    assert name_row["row_1"] == "Bob"


def test_transpose_empty_rows_raises():
    with pytest.raises(TransposerError, match="no rows"):
        transpose(HEADERS, [])


def test_transpose_empty_headers_raises():
    with pytest.raises(TransposerError, match="no columns"):
        transpose([], ROWS)


def test_transpose_single_row():
    result = transpose(["a", "b"], [{"a": "1", "b": "2"}])
    assert result.headers == ["field", "row_0"]
    assert len(result.rows) == 2


# --- CLI tests ---


def _write_csv(tmp_path, name, headers, rows):
    p = tmp_path / name
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=headers, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return str(p)


def _args(input_path, output="-", verbose=False):
    ns = types.SimpleNamespace()
    ns.input = input_path
    ns.output = output
    ns.verbose = verbose
    return ns


def test_cmd_transpose_exits_zero(tmp_path, capsys):
    p = _write_csv(tmp_path, "data.csv", HEADERS, ROWS)
    rc = cmd_transpose(_args(p))
    assert rc == 0


def test_cmd_transpose_stdout_contains_field_column(tmp_path, capsys):
    p = _write_csv(tmp_path, "data.csv", HEADERS, ROWS)
    cmd_transpose(_args(p))
    out = capsys.readouterr().out
    assert "field" in out


def test_cmd_transpose_verbose_prints_summary(tmp_path, capsys):
    p = _write_csv(tmp_path, "data.csv", HEADERS, ROWS)
    cmd_transpose(_args(p, verbose=True))
    err = capsys.readouterr().err
    assert "Transposed" in err


def test_cmd_transpose_writes_file(tmp_path):
    p = _write_csv(tmp_path, "in.csv", HEADERS, ROWS)
    out_path = str(tmp_path / "out.csv")
    cmd_transpose(_args(p, output=out_path))
    with open(out_path, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    assert rows[0]["field"] == "id"
