"""Integration tests for the interpolate CLI command."""
import csv
import io
import os
import sys
import types

import pytest

from csvdiff.cli_interpolate import cmd_interpolate


def _write_csv(path, rows, headers):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp_csv(tmp_path):
    p = tmp_path / "data.csv"
    rows = [
        {"id": "1", "value": "0.0"},
        {"id": "2", "value": ""},
        {"id": "3", "value": "6.0"},
    ]
    _write_csv(str(p), rows, ["id", "value"])
    return str(p)


def _args(**kwargs):
    defaults = {"columns": ["value"], "output": None, "quiet": False}
    defaults.update(kwargs)
    ns = types.SimpleNamespace(**defaults)
    return ns


def test_cmd_interpolate_exits_zero(tmp_csv, capsys):
    args = _args(file=tmp_csv)
    code = cmd_interpolate(args)
    assert code == 0


def test_cmd_interpolate_fills_gap(tmp_csv, capsys):
    args = _args(file=tmp_csv)
    cmd_interpolate(args)
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    rows = list(reader)
    assert float(rows[1]["value"]) == pytest.approx(3.0)


def test_cmd_interpolate_summary_printed(tmp_csv, capsys):
    args = _args(file=tmp_csv)
    cmd_interpolate(args)
    captured = capsys.readouterr()
    assert "interpolated 1 cell" in captured.err


def test_cmd_interpolate_quiet_suppresses_summary(tmp_csv, capsys):
    args = _args(file=tmp_csv, quiet=True)
    cmd_interpolate(args)
    captured = capsys.readouterr()
    assert captured.err == ""


def test_cmd_interpolate_writes_output_file(tmp_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _args(file=tmp_csv, output=out)
    code = cmd_interpolate(args)
    assert code == 0
    assert os.path.exists(out)
    with open(out, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert float(rows[1]["value"]) == pytest.approx(3.0)


def test_cmd_interpolate_missing_file_returns_2(tmp_path):
    args = _args(file=str(tmp_path / "nope.csv"))
    with pytest.raises(SystemExit) as exc_info:
        cmd_interpolate(args)
    assert exc_info.value.code == 2


def test_cmd_interpolate_unknown_column_returns_1(tmp_csv, capsys):
    args = _args(file=tmp_csv, columns=["nonexistent"])
    code = cmd_interpolate(args)
    assert code == 1
    captured = capsys.readouterr()
    assert "nonexistent" in captured.err
