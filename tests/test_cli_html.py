"""Tests for csvdiff.cli_html."""
import csv
import io
import sys
from pathlib import Path

import pytest

from csvdiff.cli_html import cmd_html


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
    _write_csv(left, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}])
    _write_csv(right, [{"id": "1", "name": "Alice"}, {"id": "3", "name": "Carol"}])
    return left, right


class _Args:
    def __init__(self, left, right, **kwargs):
        self.left = str(left)
        self.right = str(right)
        self.keys = kwargs.get("keys", [])
        self.title = kwargs.get("title", "CSV Diff Report")
        self.max_rows = kwargs.get("max_rows", 200)
        self.show_unchanged = kwargs.get("show_unchanged", False)
        self.output = kwargs.get("output", "-")


def test_cmd_html_exits_zero(tmp_pair, capsys):
    left, right = tmp_pair
    args = _Args(left, right)
    code = cmd_html(args)
    assert code == 0


def test_cmd_html_stdout_contains_doctype(tmp_pair, capsys):
    left, right = tmp_pair
    args = _Args(left, right)
    cmd_html(args)
    out = capsys.readouterr().out
    assert "<!DOCTYPE html>" in out


def test_cmd_html_custom_title(tmp_pair, capsys):
    left, right = tmp_pair
    args = _Args(left, right, title="My Custom Title")
    cmd_html(args)
    out = capsys.readouterr().out
    assert "My Custom Title" in out


def test_cmd_html_writes_file(tmp_pair, tmp_path):
    left, right = tmp_pair
    out_file = tmp_path / "report.html"
    args = _Args(left, right, output=str(out_file))
    code = cmd_html(args)
    assert code == 0
    content = out_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content


def test_cmd_html_missing_file_returns_2(tmp_path):
    left = tmp_path / "missing.csv"
    right = tmp_path / "also_missing.csv"
    args = _Args(left, right)
    code = cmd_html(args)
    assert code == 2


def test_cmd_html_show_unchanged_flag(tmp_pair, capsys):
    left, right = tmp_pair
    args = _Args(left, right, show_unchanged=True)
    cmd_html(args)
    out = capsys.readouterr().out
    assert 'csvdiff-unchanged' in out
