"""Tests for csvdiff.cli_sample."""
import csv
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from csvdiff.cli_sample import cmd_sample


def _write_csv(path: Path, rows, fieldnames=None):
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


@pytest.fixture()
def tmp_pair(tmp_path):
    left_rows = [{"id": str(i), "val": str(i * 2)} for i in range(30)]
    right_rows = [
        {"id": str(i), "val": str(i * 2 + (1 if i < 5 else 0))} for i in range(25)
    ] + [{"id": "99", "val": "extra"}]
    left = tmp_path / "left.csv"
    right = tmp_path / "right.csv"
    _write_csv(left, left_rows)
    _write_csv(right, right_rows)
    return str(left), str(right)


def _args(left, right, **kwargs):
    defaults = dict(
        left=left, right=right, key=["id"], count=5, frac=None,
        seed=42, include_unchanged=False, fmt="text"
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_cmd_sample_text_exit_zero(tmp_pair, capsys):
    left, right = tmp_pair
    rc = cmd_sample(_args(left, right))
    assert rc == 0


def test_cmd_sample_json_output(tmp_pair, capsys):
    left, right = tmp_pair
    rc = cmd_sample(_args(left, right, fmt="json"))
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "added" in data
    assert "removed" in data
    assert "modified" in data


def test_cmd_sample_json_respects_n(tmp_pair, capsys):
    left, right = tmp_pair
    cmd_sample(_args(left, right, fmt="json", count=2))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data["added"]) <= 2
    assert len(data["modified"]) <= 2


def test_cmd_sample_frac(tmp_pair, capsys):
    left, right = tmp_pair
    rc = cmd_sample(_args(left, right, fmt="json", frac=0.5, count=None))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data["added"], list)


def test_cmd_sample_missing_file_returns_2(tmp_path, capsys):
    rc = cmd_sample(_args("no.csv", "no2.csv"))
    assert rc == 2


def test_cmd_sample_invalid_n_returns_1(tmp_pair, capsys):
    left, right = tmp_pair
    rc = cmd_sample(_args(left, right, count=-1))
    assert rc == 1


def test_cmd_sample_include_unchanged_json(tmp_pair, capsys):
    left, right = tmp_pair
    rc = cmd_sample(_args(left, right, fmt="json", include_unchanged=True))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "unchanged" in data
