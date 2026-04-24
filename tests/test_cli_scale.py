"""Tests for csvdiff.cli_scale."""
import csv
import io
import os
import pytest

from csvdiff.cli_scale import cmd_scale


def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def tmp_csv(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(
        str(p),
        [
            {"id": "1", "value": "10"},
            {"id": "2", "value": "20"},
            {"id": "3", "value": "30"},
        ],
    )
    return str(p)


class _Args:
    def __init__(self, file, column, method="minmax", output=None, stats=False):
        self.file = file
        self.column = column
        self.method = method
        self.output = output
        self.stats = stats


def test_cmd_scale_exits_zero(tmp_csv):
    args = _Args(tmp_csv, "value")
    assert cmd_scale(args) == 0


def test_cmd_scale_zscore_exits_zero(tmp_csv):
    args = _Args(tmp_csv, "value", method="zscore")
    assert cmd_scale(args) == 0


def test_cmd_scale_missing_file_returns_2():
    args = _Args("no_such_file.csv", "value")
    assert cmd_scale(args) == 2


def test_cmd_scale_bad_column_returns_1(tmp_csv):
    args = _Args(tmp_csv, "nonexistent")
    assert cmd_scale(args) == 1


def test_cmd_scale_writes_output(tmp_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _Args(tmp_csv, "value", output=out)
    cmd_scale(args)
    assert os.path.exists(out)
    with open(out, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 3
    assert "value" in rows[0]


def test_cmd_scale_minmax_range(tmp_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _Args(tmp_csv, "value", output=out)
    cmd_scale(args)
    with open(out, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    values = [float(r["value"]) for r in rows]
    assert min(values) == pytest.approx(0.0)
    assert max(values) == pytest.approx(1.0)


def test_cmd_scale_stats_flag_exits_zero(tmp_csv, capsys):
    args = _Args(tmp_csv, "value", stats=True)
    rc = cmd_scale(args)
    assert rc == 0
