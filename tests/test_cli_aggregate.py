"""Tests for csvdiff.cli_aggregate."""
import csv
import io
import json
import os
import types

import pytest

from csvdiff.cli_aggregate import cmd_aggregate


def _write_csv(tmp_path, rows, filename="data.csv"):
    path = tmp_path / filename
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


ROWS = [
    {"name": "Alice", "score": "10", "age": "30"},
    {"name": "Bob", "score": "20", "age": "25"},
    {"name": "Carol", "score": "30", "age": "35"},
]


def _args(file, columns, fmt="text"):
    ns = types.SimpleNamespace(file=file, columns=columns, fmt=fmt)
    return ns


def test_cmd_aggregate_text_exit_zero(tmp_path):
    path = _write_csv(tmp_path, ROWS)
    assert cmd_aggregate(_args(path, ["score"])) == 0


def test_cmd_aggregate_json_exit_zero(tmp_path):
    path = _write_csv(tmp_path, ROWS)
    assert cmd_aggregate(_args(path, ["score"], fmt="json")) == 0


def test_cmd_aggregate_json_content(tmp_path, capsys):
    path = _write_csv(tmp_path, ROWS)
    cmd_aggregate(_args(path, ["score"], fmt="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "score" in data
    assert data["score"]["count"] == 3
    assert data["score"]["total"] == pytest.approx(60.0)
    assert data["score"]["mean"] == pytest.approx(20.0)


def test_cmd_aggregate_text_content(tmp_path, capsys):
    path = _write_csv(tmp_path, ROWS)
    cmd_aggregate(_args(path, ["age"]))
    out = capsys.readouterr().out
    assert "[age]" in out
    assert "count" in out


def test_cmd_aggregate_missing_file_returns_2(tmp_path):
    rc = cmd_aggregate(_args(str(tmp_path / "nope.csv"), ["score"]))
    assert rc == 2


def test_cmd_aggregate_unknown_column_returns_1(tmp_path):
    path = _write_csv(tmp_path, ROWS)
    rc = cmd_aggregate(_args(path, ["nonexistent"]))
    assert rc == 1


def test_cmd_aggregate_multiple_columns_json(tmp_path, capsys):
    path = _write_csv(tmp_path, ROWS)
    cmd_aggregate(_args(path, ["score", "age"], fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert "score" in data and "age" in data
