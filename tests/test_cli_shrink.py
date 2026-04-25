"""Tests for csvdiff.cli_shrink."""
import csv
import io
import os
import pytest

from csvdiff.cli_shrink import cmd_shrink


def _write_csv(path, rows):
    headers = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def tmp_csv(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(str(p), [
        {"id": "1", "name": "Alice",                 "note": "short"},
        {"id": "2", "name": "Bob",                   "note": "a very long note that exceeds the limit"},
        {"id": "3", "name": "Christopher Columbus", "note": "medium note here"},
    ])
    return str(p)


class _Args:
    def __init__(self, file, column, max_length, ellipsis="...", output="", stats=False):
        self.file = file
        self.column = column
        self.max_length = max_length
        self.ellipsis = ellipsis
        self.output = output
        self.stats = stats


def test_cmd_shrink_exits_zero(tmp_csv):
    args = _Args(tmp_csv, "note", 10)
    assert cmd_shrink(args) == 0


def test_cmd_shrink_missing_file_returns_2(tmp_path):
    args = _Args(str(tmp_path / "missing.csv"), "note", 10)
    assert cmd_shrink(args) == 2


def test_cmd_shrink_unknown_column_returns_1(tmp_csv):
    args = _Args(tmp_csv, "nonexistent", 10)
    assert cmd_shrink(args) == 1


def test_cmd_shrink_invalid_max_length_returns_1(tmp_csv):
    args = _Args(tmp_csv, "note", 0)
    assert cmd_shrink(args) == 1


def test_cmd_shrink_writes_output_file(tmp_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _Args(tmp_csv, "note", 10, output=out)
    assert cmd_shrink(args) == 0
    assert os.path.exists(out)
    with open(out, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    assert all(len(r["note"]) <= 10 for r in rows)


def test_cmd_shrink_long_value_truncated(tmp_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _Args(tmp_csv, "note", 10, output=out)
    cmd_shrink(args)
    with open(out, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    long_row = next(r for r in rows if r["id"] == "2")
    assert long_row["note"].endswith("...")
    assert len(long_row["note"]) == 10


def test_cmd_shrink_custom_ellipsis(tmp_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _Args(tmp_csv, "note", 8, ellipsis="~~", output=out)
    cmd_shrink(args)
    with open(out, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    long_row = next(r for r in rows if r["id"] == "2")
    assert long_row["note"].endswith("~~")
