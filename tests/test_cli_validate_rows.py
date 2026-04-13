"""Tests for csvdiff.cli_validate_rows."""

import csv
import io
import json
import os
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from csvdiff.cli_validate_rows import cmd_validate_rows


def _write_csv(path: Path, rows: list, fieldnames: list) -> None:
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp_csv(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(
        p,
        [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}],
        ["name", "age"],
    )
    return p


@pytest.fixture()
def bad_csv(tmp_path):
    p = tmp_path / "bad.csv"
    _write_csv(
        p,
        [{"name": "", "age": "notanint"}, {"name": "Bob", "age": "25"}],
        ["name", "age"],
    )
    return p


def _args(file, rules=None, fmt="text"):
    return SimpleNamespace(file=str(file), rules=rules or [], format=fmt)


def test_valid_file_exits_zero(tmp_csv):
    args = _args(tmp_csv, rules=["name:nonempty", "age:integer"])
    assert cmd_validate_rows(args) == 0


def test_invalid_file_exits_one(bad_csv):
    args = _args(bad_csv, rules=["name:nonempty", "age:integer"])
    assert cmd_validate_rows(args) == 1


def test_missing_file_exits_two(tmp_path):
    args = _args(tmp_path / "missing.csv", rules=["name:nonempty"])
    assert cmd_validate_rows(args) == 2


def test_bad_rule_format_exits_two(tmp_csv):
    args = _args(tmp_csv, rules=["bad_rule_no_colon"])
    assert cmd_validate_rows(args) == 2


def test_unknown_rule_exits_two(tmp_csv):
    args = _args(tmp_csv, rules=["name:nonexistent"])
    assert cmd_validate_rows(args) == 2


def test_json_output_valid(tmp_csv, capsys):
    args = _args(tmp_csv, rules=["name:nonempty"], fmt="json")
    rc = cmd_validate_rows(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["valid"] is True
    assert data["violations"] == []
    assert rc == 0


def test_json_output_violations(bad_csv, capsys):
    args = _args(bad_csv, rules=["name:nonempty", "age:integer"], fmt="json")
    rc = cmd_validate_rows(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["valid"] is False
    assert len(data["violations"]) >= 1
    assert rc == 1


def test_text_output_ok(tmp_csv, capsys):
    args = _args(tmp_csv, rules=["name:nonempty"])
    cmd_validate_rows(args)
    captured = capsys.readouterr()
    assert "OK" in captured.out


def test_text_output_shows_violations(bad_csv, capsys):
    args = _args(bad_csv, rules=["name:nonempty"])
    cmd_validate_rows(args)
    captured = capsys.readouterr()
    assert "nonempty" in captured.out
