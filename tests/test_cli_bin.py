import csv
import io
import json
import os
import pytest
from csvdiff.cli_bin import cmd_bin


def _write_csv(path, rows, headers):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def tmp_csv(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(
        p,
        [{"id": str(i), "score": str(i * 10)} for i in range(1, 11)],
        ["id", "score"],
    )
    return str(p)


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _args(path, **kw):
    defaults = dict(
        file=path,
        column="score",
        boundaries=["0", "50", "100"],
        labels=[],
        bin_column="",
        out_of_range="other",
        format="csv",
    )
    defaults.update(kw)
    return _Args(**defaults)


def test_cmd_bin_exits_zero(tmp_csv, capsys):
    assert cmd_bin(_args(tmp_csv)) == 0


def test_cmd_bin_csv_output_has_bin_column(tmp_csv, capsys):
    cmd_bin(_args(tmp_csv))
    out = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert "score_bin" in rows[0]


def test_cmd_bin_json_output(tmp_csv, capsys):
    cmd_bin(_args(tmp_csv, format="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert "score_bin" in data[0]


def test_cmd_bin_stats_output(tmp_csv, capsys):
    cmd_bin(_args(tmp_csv, format="stats"))
    out = capsys.readouterr().out
    assert ":" in out


def test_cmd_bin_missing_file_returns_2(capsys):
    rc = cmd_bin(_args("no_such_file.csv"))
    assert rc == 2


def test_cmd_bin_bad_column_returns_1(tmp_csv, capsys):
    rc = cmd_bin(_args(tmp_csv, column="nonexistent"))
    assert rc == 1


def test_cmd_bin_custom_labels(tmp_csv, capsys):
    cmd_bin(_args(tmp_csv, labels=["low", "high"]))
    out = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(out))
    values = {r["score_bin"] for r in reader}
    assert values <= {"low", "high", "other"}
