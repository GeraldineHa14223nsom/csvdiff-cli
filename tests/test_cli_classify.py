"""Tests for csvdiff.cli_classify."""
import csv
import io
import json
import os
import tempfile

import pytest

from csvdiff.cli_classify import cmd_classify


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
            {"name": "Alice", "score": "92"},
            {"name": "Bob", "score": "45"},
            {"name": "Carol", "score": "73"},
        ],
    )
    return str(p)


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _args(tmp_csv, **kw):
    defaults = dict(
        file=tmp_csv,
        column="score",
        rule=["high:80-100", "mid:50-79", "low:0-49"],
        label_column="label",
        default=None,
        format="csv",
        quiet=True,
    )
    defaults.update(kw)
    return _Args(**defaults)


def test_cmd_classify_exits_zero(tmp_csv, capsys):
    rc = cmd_classify(_args(tmp_csv))
    assert rc == 0


def test_cmd_classify_stdout_has_label_column(tmp_csv, capsys):
    cmd_classify(_args(tmp_csv))
    out = capsys.readouterr().out
    assert "label" in out


def test_cmd_classify_json_output(tmp_csv, capsys):
    rc = cmd_classify(_args(tmp_csv, format="json"))
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert "label" in data[0]


def test_cmd_classify_missing_file_returns_2(capsys):
    rc = cmd_classify(_args("/no/such/file.csv"))
    assert rc == 2


def test_cmd_classify_bad_column_returns_1(tmp_csv, capsys):
    rc = cmd_classify(_args(tmp_csv, column="nonexistent"))
    assert rc == 1


def test_cmd_classify_pattern_rule(tmp_csv, capsys):
    rc = cmd_classify(
        _args(tmp_csv, column="name", rule=["alice_group:^Alice$", "rest:.*"])
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "alice_group" in out


def test_cmd_classify_default_label(tmp_csv, capsys):
    rc = cmd_classify(
        _args(tmp_csv, rule=["high:90-100"], default="other")
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "other" in out
