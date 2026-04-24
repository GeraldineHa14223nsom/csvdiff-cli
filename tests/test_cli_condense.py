"""Tests for csvdiff.cli_condense."""
import csv
import io
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from csvdiff.cli_condense import cmd_condense


def _write_csv(path: str, rows: list, headers: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def tmp_csv(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(
        str(p),
        [
            {"id": "1", "name": "Alice", "tag": "python"},
            {"id": "1", "name": "Alice", "tag": "data"},
            {"id": "2", "name": "Bob",   "tag": "java"},
            {"id": "2", "name": "Bob",   "tag": "spring"},
        ],
        ["id", "name", "tag"],
    )
    return str(p)


def _args(tmp_csv, **kwargs):
    defaults = dict(
        input=tmp_csv,
        key=["id"],
        agg_column="tag",
        separator="|",
        output="",
        quiet=True,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_condense_exits_zero(tmp_csv, capsys):
    rc = cmd_condense(_args(tmp_csv))
    assert rc == 0


def test_cmd_condense_stdout_output(tmp_csv, capsys):
    rc = cmd_condense(_args(tmp_csv))
    assert rc == 0
    captured = capsys.readouterr()
    assert "python|data" in captured.out


def test_cmd_condense_writes_file(tmp_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    rc = cmd_condense(_args(tmp_csv, output=out))
    assert rc == 0
    assert os.path.exists(out)
    with open(out, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    assert len(rows) == 2


def test_cmd_condense_custom_separator(tmp_csv, capsys):
    rc = cmd_condense(_args(tmp_csv, separator=","))
    assert rc == 0
    captured = capsys.readouterr()
    assert "python,data" in captured.out


def test_cmd_condense_missing_file_exits_2(tmp_path):
    args = SimpleNamespace(
        input=str(tmp_path / "ghost.csv"),
        key=["id"],
        agg_column="tag",
        separator="|",
        output="",
        quiet=True,
    )
    with pytest.raises(SystemExit) as exc_info:
        cmd_condense(args)
    assert exc_info.value.code == 2


def test_cmd_condense_bad_key_returns_2(tmp_csv):
    rc = cmd_condense(_args(tmp_csv, key=["missing"]))
    assert rc == 2


def test_cmd_condense_summary_printed(tmp_csv, capsys):
    rc = cmd_condense(_args(tmp_csv, quiet=False))
    assert rc == 0
    captured = capsys.readouterr()
    assert "condensed" in captured.err
    assert "→" in captured.err
