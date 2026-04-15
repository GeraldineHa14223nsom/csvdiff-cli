"""Integration tests for the group CLI command."""
import csv
import io
import json
import os
import tempfile

import pytest

from csvdiff.cli_group import cmd_group


def _write_csv(path: str, rows) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp_csv(tmp_path):
    rows = [
        {"dept": "eng", "name": "Alice", "salary": "90000"},
        {"dept": "eng", "name": "Bob",   "salary": "85000"},
        {"dept": "hr",  "name": "Carol", "salary": "70000"},
    ]
    p = tmp_path / "data.csv"
    _write_csv(str(p), rows)
    return str(p)


class _Args:
    def __init__(self, file, keys, agg_column="", agg_func="count", format="text"):
        self.file = file
        self.keys = keys
        self.agg_column = agg_column
        self.agg_func = agg_func
        self.format = format


def test_cmd_group_text_exit_zero(tmp_csv):
    args = _Args(tmp_csv, "dept")
    assert cmd_group(args) == 0


def test_cmd_group_json_exit_zero(tmp_csv):
    args = _Args(tmp_csv, "dept", format="json")
    assert cmd_group(args) == 0


def test_cmd_group_json_content(tmp_csv, capsys):
    args = _Args(tmp_csv, "dept", format="json")
    cmd_group(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["group_count"] == 2
    assert data["row_count"] == 3


def test_cmd_group_agg_total(tmp_csv, capsys):
    args = _Args(tmp_csv, "dept", agg_column="salary", agg_func="total", format="json")
    rc = cmd_group(args)
    assert rc == 0
    out = capsys.readouterr().out
    rows = json.loads(out)
    totals = {r["dept"]: float(r["total_salary"]) for r in rows}
    assert totals["eng"] == pytest.approx(175000.0)


def test_cmd_group_missing_file_returns_2(tmp_path):
    args = _Args(str(tmp_path / "missing.csv"), "dept")
    assert cmd_group(args) == 2


def test_cmd_group_unknown_key_returns_1(tmp_csv):
    args = _Args(tmp_csv, "nonexistent")
    assert cmd_group(args) == 1
