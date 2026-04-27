"""Tests for csvdiff.cli_excel."""
from __future__ import annotations

import csv
import io
from pathlib import Path

import pytest

from csvdiff.cli_excel import cmd_excel


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp_pair(tmp_path):
    left = tmp_path / "left.csv"
    right = tmp_path / "right.csv"
    _write_csv(left, [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
    ])
    _write_csv(right, [
        {"id": "1", "name": "Alicia"},
        {"id": "3", "name": "Carol"},
    ])
    return left, right


class _Args:
    def __init__(self, left, right, keys=None, max_col_width=64,
                 include_unchanged=False, output="-"):
        self.left = str(left)
        self.right = str(right)
        self.keys = keys or ["id"]
        self.max_col_width = max_col_width
        self.include_unchanged = include_unchanged
        self.output = output


def test_cmd_excel_exits_zero(tmp_pair, capsys):
    left, right = tmp_pair
    rc = cmd_excel(_Args(left, right))
    assert rc == 0


def test_cmd_excel_stdout_contains_added(tmp_pair, capsys):
    left, right = tmp_pair
    cmd_excel(_Args(left, right))
    out = capsys.readouterr().out
    assert "Carol" in out


def test_cmd_excel_stdout_contains_removed(tmp_pair, capsys):
    left, right = tmp_pair
    cmd_excel(_Args(left, right))
    out = capsys.readouterr().out
    assert "Bob" in out


def test_cmd_excel_missing_left_returns_2(tmp_pair):
    _, right = tmp_pair
    rc = cmd_excel(_Args("/no/such/file.csv", right))
    assert rc == 2


def test_cmd_excel_missing_right_returns_2(tmp_pair):
    left, _ = tmp_pair
    rc = cmd_excel(_Args(left, "/no/such/file.csv"))
    assert rc == 2


def test_cmd_excel_writes_to_file(tmp_pair, tmp_path):
    left, right = tmp_pair
    out_file = tmp_path / "out.csv"
    rc = cmd_excel(_Args(left, right, output=str(out_file)))
    assert rc == 0
    content = out_file.read_text()
    assert "## Added" in content
