"""Tests for csvdiff.cli_replace."""
import csv
import io
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from csvdiff.cli_replace import cmd_replace


def _write_csv(path: Path, rows, headers) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp_csv(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(
        p,
        [
            {"id": "1", "name": "Alice", "city": "New York"},
            {"id": "2", "name": "Bob", "city": "Boston"},
        ],
        ["id", "name", "city"],
    )
    return str(p)


def _args(tmp_csv, **kwargs):
    defaults = dict(
        file=tmp_csv,
        column="city",
        pattern="New York",
        replacement="NYC",
        regex=False,
        ignore_case=False,
        verbose=False,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_replace_exits_zero(tmp_csv, capsys):
    rc = cmd_replace(_args(tmp_csv))
    assert rc == 0


def test_cmd_replace_stdout_contains_header(tmp_csv, capsys):
    cmd_replace(_args(tmp_csv))
    out = capsys.readouterr().out
    assert "city" in out


def test_cmd_replace_value_in_output(tmp_csv, capsys):
    cmd_replace(_args(tmp_csv))
    out = capsys.readouterr().out
    assert "NYC" in out


def test_cmd_replace_missing_file_returns_2(tmp_csv, capsys):
    args = _args("/no/such/file.csv")
    rc = cmd_replace(args)
    assert rc == 2


def test_cmd_replace_bad_column_returns_1(tmp_csv, capsys):
    args = _args(tmp_csv, column="country")
    rc = cmd_replace(args)
    assert rc == 1


def test_cmd_replace_verbose_prints_to_stderr(tmp_csv, capsys):
    cmd_replace(_args(tmp_csv, verbose=True))
    err = capsys.readouterr().err
    assert "Replaced" in err


def test_cmd_replace_regex_mode(tmp_csv, capsys):
    cmd_replace(_args(tmp_csv, pattern=r"New\s+York", replacement="NYC", regex=True))
    out = capsys.readouterr().out
    assert "NYC" in out


def test_cmd_replace_ignore_case(tmp_csv, tmp_path, capsys):
    p = tmp_path / "lower.csv"
    _write_csv(
        p,
        [{"id": "1", "city": "new york"}, {"id": "2", "city": "Boston"}],
        ["id", "city"],
    )
    args = _args(str(p), column="city", pattern="New York", ignore_case=True)
    rc = cmd_replace(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "NYC" in out
