"""Tests for csvdiff.cli_bucket."""
import csv
import io
import json
import os

import pytest

from csvdiff.cli_bucket import cmd_bucket


def _write_csv(path, rows, headers=None):
    headers = headers or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp_csv(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(
        str(p),
        [
            {"name": "Alice", "score": "25"},
            {"name": "Bob", "score": "60"},
            {"name": "Carol", "score": "85"},
        ],
    )
    return str(p)


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _args(tmp_csv, **overrides):
    defaults = dict(
        file=tmp_csv,
        column="score",
        bucket=["low:0:50", "mid:50:75", "high:75:100"],
        label_column="bucket",
        default_label="other",
        output=None,
        format="csv",
    )
    defaults.update(overrides)
    return _Args(**defaults)


def test_cmd_bucket_exits_zero(tmp_csv, capsys):
    rc = cmd_bucket(_args(tmp_csv))
    assert rc == 0


def test_cmd_bucket_csv_output_has_bucket_column(tmp_csv, capsys):
    cmd_bucket(_args(tmp_csv))
    out = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert all("bucket" in r for r in rows)


def test_cmd_bucket_json_output(tmp_csv, capsys):
    rc = cmd_bucket(_args(tmp_csv, format="json"))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "rows" in data
    assert "bucket_counts" in data


def test_cmd_bucket_writes_to_file(tmp_csv, tmp_path):
    out_path = str(tmp_path / "out.csv")
    rc = cmd_bucket(_args(tmp_csv, output=out_path))
    assert rc == 0
    assert os.path.exists(out_path)
    with open(out_path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert all("bucket" in r for r in rows)


def test_missing_file_returns_2(tmp_path):
    rc = cmd_bucket(_args(str(tmp_path / "missing.csv")))
    assert rc == 2


def test_bad_bucket_spec_returns_1(tmp_csv, capsys):
    rc = cmd_bucket(_args(tmp_csv, bucket=["bad-spec"]))
    assert rc == 1


def test_unknown_column_returns_1(tmp_csv, capsys):
    rc = cmd_bucket(_args(tmp_csv, column="nonexistent"))
    assert rc == 1
