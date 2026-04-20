"""Tests for csvdiff.cli_sentinel."""
import csv
import io
import json
import os
import tempfile

import pytest

from csvdiff.cli_sentinel import cmd_sentinel


def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def tmp_csv(tmp_path):
    rows = [
        {"id": "1", "name": "Alice", "score": "10"},
        {"id": "2", "name": "", "score": "-3"},
        {"id": "3", "name": "Bob", "score": "abc"},
    ]
    p = tmp_path / "data.csv"
    _write_csv(str(p), rows)
    return str(p)


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _args(tmp_csv, **kw):
    defaults = dict(
        file=tmp_csv,
        rule=None,
        label_column=None,
        output=None,
        format="text",
    )
    defaults.update(kw)
    return _Args(**defaults)


def test_cmd_sentinel_exits_zero_no_rules(tmp_csv):
    code = cmd_sentinel(_args(tmp_csv))
    assert code == 0


def test_cmd_sentinel_exits_one_on_match(tmp_csv):
    code = cmd_sentinel(_args(tmp_csv, rule=["name:nonempty"]))
    assert code == 1


def test_cmd_sentinel_json_output(tmp_csv, capsys):
    cmd_sentinel(_args(tmp_csv, rule=["name:nonempty"], format="json"))
    captured = capsys.readouterr().out
    data = json.loads(captured)
    assert "match_count" in data
    assert data["match_count"] == 1


def test_cmd_sentinel_text_output(tmp_csv, capsys):
    cmd_sentinel(_args(tmp_csv, rule=["name:nonempty"]))
    out = capsys.readouterr().out
    assert "Matches" in out


def test_cmd_sentinel_missing_file_returns_2(tmp_path):
    with pytest.raises(SystemExit) as exc:
        cmd_sentinel(_args(str(tmp_path / "missing.csv")))
    assert exc.value.code == 2


def test_cmd_sentinel_bad_rule_spec_returns_2(tmp_csv):
    code = cmd_sentinel(_args(tmp_csv, rule=["badspec"]))
    assert code == 2


def test_cmd_sentinel_writes_output_file(tmp_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    cmd_sentinel(_args(tmp_csv, rule=["name:nonempty"], label_column="_flag", output=out))
    assert os.path.exists(out)
    with open(out, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    assert "_flag" in rows[0]
