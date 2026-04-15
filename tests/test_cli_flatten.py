"""Tests for csvdiff.cli_flatten."""
import csv
import io
import os
import types

import pytest

from csvdiff.cli_flatten import cmd_flatten


def _write_csv(path: str, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp_csv(tmp_path):
    rows = [
        {"id": "1", "info": '{"score": 99, "grade": "A"}'},
        {"id": "2", "info": '{"score": 72, "grade": "B"}'},
    ]
    p = tmp_path / "data.csv"
    _write_csv(str(p), rows)
    return str(p)


def _args(**kwargs):
    defaults = dict(
        file=None,
        column="info",
        prefix="",
        drop_source=False,
        output=None,
        verbose=False,
    )
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def test_cmd_flatten_exits_zero(tmp_csv):
    args = _args(file=tmp_csv)
    assert cmd_flatten(args) == 0


def test_cmd_flatten_missing_file_returns_2(tmp_path):
    args = _args(file=str(tmp_path / "ghost.csv"))
    assert cmd_flatten(args) == 2


def test_cmd_flatten_bad_column_returns_1(tmp_csv):
    args = _args(file=tmp_csv, column="nope")
    assert cmd_flatten(args) == 1


def test_cmd_flatten_writes_output(tmp_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _args(file=tmp_csv, output=out)
    cmd_flatten(args)
    assert os.path.exists(out)
    with open(out, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    assert "score" in reader.fieldnames
    assert rows[0]["score"] == "99"


def test_cmd_flatten_drop_source(tmp_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _args(file=tmp_csv, drop_source=True, output=out)
    cmd_flatten(args)
    with open(out, newline="") as fh:
        reader = csv.DictReader(fh)
        list(reader)
    assert "info" not in reader.fieldnames


def test_cmd_flatten_prefix(tmp_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _args(file=tmp_csv, prefix="x_", output=out)
    cmd_flatten(args)
    with open(out, newline="") as fh:
        reader = csv.DictReader(fh)
        list(reader)
    assert "x_score" in reader.fieldnames
