"""Integration tests for csvdiff.cli_stack."""
import csv
import io
import os
import sys
import pytest
from csvdiff.cli_stack import cmd_stack


def _write_csv(path, headers, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp_pair(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(str(a), ["id", "name"], [{"id": "1", "name": "Alice"}])
    _write_csv(str(b), ["id", "name"], [{"id": "2", "name": "Bob"}])
    return str(a), str(b), tmp_path


class _Args:
    def __init__(self, files, output=None, no_strict=False, fill_value="", summary=False):
        self.files = files
        self.output = output
        self.no_strict = no_strict
        self.fill_value = fill_value
        self.summary = summary


def test_stack_exits_zero(tmp_pair, capsys):
    a, b, _ = tmp_pair
    args = _Args(files=[a, b])
    assert cmd_stack(args) == 0


def test_stack_stdout_contains_rows(tmp_pair, capsys):
    a, b, _ = tmp_pair
    args = _Args(files=[a, b])
    cmd_stack(args)
    captured = capsys.readouterr()
    assert "Alice" in captured.out
    assert "Bob" in captured.out


def test_stack_writes_output_file(tmp_pair):
    a, b, tmp_path = tmp_pair
    out = str(tmp_path / "out.csv")
    args = _Args(files=[a, b], output=out)
    cmd_stack(args)
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2


def test_stack_summary_to_stderr(tmp_pair, capsys):
    a, b, _ = tmp_pair
    args = _Args(files=[a, b], summary=True)
    cmd_stack(args)
    captured = capsys.readouterr()
    assert "2" in captured.err


def test_stack_strict_error_returns_1(tmp_path, capsys):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(str(a), ["id", "name"], [{"id": "1", "name": "Alice"}])
    _write_csv(str(b), ["id", "email"], [{"id": "2", "email": "b@x.com"}])
    args = _Args(files=[str(a), str(b)], no_strict=False)
    assert cmd_stack(args) == 1


def test_stack_no_strict_succeeds_with_different_columns(tmp_path, capsys):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    _write_csv(str(a), ["id", "name"], [{"id": "1", "name": "Alice"}])
    _write_csv(str(b), ["id", "email"], [{"id": "2", "email": "b@x.com"}])
    args = _Args(files=[str(a), str(b)], no_strict=True, fill_value="")
    assert cmd_stack(args) == 0


def test_stack_too_few_files_returns_2(tmp_pair, capsys):
    a, _, _ = tmp_pair
    args = _Args(files=[a])
    assert cmd_stack(args) == 2
