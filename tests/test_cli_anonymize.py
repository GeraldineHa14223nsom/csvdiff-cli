"""Tests for csvdiff.cli_anonymize."""
import csv
import io
import sys
import pytest
from unittest.mock import patch
from csvdiff.cli_anonymize import cmd_anonymize


def _write_csv(path, rows, headers):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)


@pytest.fixture
def tmp_csv(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(p, [
        {"id": "1", "name": "Alice", "email": "alice@example.com"},
        {"id": "2", "name": "Bob", "email": "bob@example.com"},
    ], ["id", "name", "email"])
    return str(p)


class _Args:
    def __init__(self, file, columns, method="hash", salt="", mask_char="*", keep=0):
        self.file = file
        self.columns = columns
        self.method = method
        self.salt = salt
        self.mask_char = mask_char
        self.keep = keep


def test_cmd_anonymize_exits_zero(tmp_csv, capsys):
    args = _Args(tmp_csv, ["email"])
    assert cmd_anonymize(args) == 0


def test_cmd_anonymize_output_is_csv(tmp_csv, capsys):
    args = _Args(tmp_csv, ["email"])
    cmd_anonymize(args)
    out = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert len(rows) == 2
    assert "email" in rows[0]


def test_cmd_anonymize_email_changed(tmp_csv, capsys):
    args = _Args(tmp_csv, ["email"])
    cmd_anonymize(args)
    out = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert rows[0]["email"] != "alice@example.com"


def test_cmd_anonymize_mask_method(tmp_csv, capsys):
    args = _Args(tmp_csv, ["name"], method="mask")
    cmd_anonymize(args)
    out = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert "*" in rows[0]["name"]


def test_cmd_anonymize_missing_file_returns_2(capsys):
    args = _Args("nonexistent.csv", ["email"])
    assert cmd_anonymize(args) == 2


def test_cmd_anonymize_bad_column_returns_1(tmp_csv, capsys):
    args = _Args(tmp_csv, ["nonexistent"])
    assert cmd_anonymize(args) == 1
