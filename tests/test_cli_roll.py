"""Tests for csvdiff.cli_roll."""
import csv
import io
import pytest
from unittest.mock import patch
from csvdiff.cli_roll import cmd_roll, build_roll_parser


def _write_csv(tmp_path, name, rows):
    p = tmp_path / name
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return str(p)


@pytest.fixture
def tmp_csv(tmp_path):
    rows = [
        {"id": "1", "val": "10"},
        {"id": "2", "val": "20"},
        {"id": "3", "val": "30"},
    ]
    return _write_csv(tmp_path, "data.csv", rows)


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_cmd_roll_exits_zero(tmp_csv, capsys):
    args = _Args(file=tmp_csv, column="val", window=2, func="mean",
                 new_column=None, output=None)
    assert cmd_roll(args) == 0


def test_cmd_roll_output_has_new_column(tmp_csv, capsys):
    args = _Args(file=tmp_csv, column="val", window=2, func="mean",
                 new_column="roll_val", output=None)
    cmd_roll(args)
    out = capsys.readouterr().out
    assert "roll_val" in out


def test_cmd_roll_missing_file_returns_2(capsys):
    args = _Args(file="/no/such/file.csv", column="val", window=2,
                 func="mean", new_column=None, output=None)
    assert cmd_roll(args) == 2


def test_cmd_roll_bad_column_returns_1(tmp_csv, capsys):
    args = _Args(file=tmp_csv, column="missing", window=2, func="mean",
                 new_column=None, output=None)
    assert cmd_roll(args) == 1


def test_cmd_roll_writes_to_file(tmp_csv, tmp_path):
    out_path = str(tmp_path / "out.csv")
    args = _Args(file=tmp_csv, column="val", window=2, func="sum",
                 new_column=None, output=out_path)
    rc = cmd_roll(args)
    assert rc == 0
    with open(out_path) as f:
        content = f.read()
    assert "val_rolling_sum_2" in content
