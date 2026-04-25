"""Tests for csvdiff.cli_sequence."""
import csv
import io
import sys
from pathlib import Path
from argparse import Namespace

import pytest

from csvdiff.cli_sequence import cmd_sequence


def _write_csv(path: Path, rows, headers) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def tmp_csv(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(
        p,
        [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}],
        ["id", "name"],
    )
    return p


def _args(file, column="seq", start=1, step=1, overwrite=False, output=None):
    return Namespace(
        file=str(file),
        column=column,
        start=start,
        step=step,
        overwrite=overwrite,
        output=output,
    )


def test_cmd_sequence_exits_zero(tmp_csv, capsys):
    rc = cmd_sequence(_args(tmp_csv))
    assert rc == 0


def test_cmd_sequence_stdout_contains_header(tmp_csv, capsys):
    cmd_sequence(_args(tmp_csv))
    captured = capsys.readouterr()
    assert "seq" in captured.out


def test_cmd_sequence_custom_column(tmp_csv, capsys):
    cmd_sequence(_args(tmp_csv, column="row_num"))
    captured = capsys.readouterr()
    assert "row_num" in captured.out


def test_cmd_sequence_values_correct(tmp_csv, capsys):
    cmd_sequence(_args(tmp_csv, start=5, step=5))
    captured = capsys.readouterr()
    assert "5" in captured.out
    assert "10" in captured.out


def test_cmd_sequence_output_file(tmp_csv, tmp_path):
    out = tmp_path / "out.csv"
    rc = cmd_sequence(_args(tmp_csv, output=str(out)))
    assert rc == 0
    assert out.exists()
    rows = list(csv.DictReader(open(out, newline="", encoding="utf-8")))
    assert rows[0]["seq"] == "1"
    assert rows[1]["seq"] == "2"


def test_cmd_sequence_missing_file_returns_2(tmp_path):
    with pytest.raises(SystemExit) as exc_info:
        cmd_sequence(_args(tmp_path / "missing.csv"))
    assert exc_info.value.code == 2


def test_cmd_sequence_existing_column_returns_1(tmp_csv, capsys):
    rc = cmd_sequence(_args(tmp_csv, column="id"))
    assert rc == 1
