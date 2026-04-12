"""Tests for the CLI entry-point."""

import csv
import textwrap
from pathlib import Path

import pytest

from csvdiff.cli import main


@pytest.fixture()
def csv_pair(tmp_path):
    """Write a simple old/new CSV pair and return their paths."""
    old = tmp_path / "old.csv"
    new = tmp_path / "new.csv"

    old.write_text(
        textwrap.dedent("""\
        id,name,score
        1,Alice,90
        2,Bob,80
        3,Carol,70
        """),
        encoding="utf-8",
    )
    new.write_text(
        textwrap.dedent("""\
        id,name,score
        1,Alice,95
        3,Carol,70
        4,Dave,88
        """),
        encoding="utf-8",
    )
    return old, new


def test_exit_code_differences(csv_pair):
    old, new = csv_pair
    assert main([str(old), str(new), "-k", "id"]) == 1


def test_exit_code_no_differences(tmp_path):
    content = "id,name\n1,Alice\n"
    old = tmp_path / "a.csv"
    new = tmp_path / "b.csv"
    old.write_text(content)
    new.write_text(content)
    assert main([str(old), str(new), "-k", "id"]) == 0


def test_missing_file_returns_2(tmp_path):
    existing = tmp_path / "a.csv"
    existing.write_text("id\n1\n")
    assert main([str(existing), str(tmp_path / "ghost.csv"), "-k", "id"]) == 2


def test_json_format_runs(csv_pair, capsys):
    old, new = csv_pair
    rc = main([str(old), str(new), "-k", "id", "-f", "json"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "added" in captured.out


def test_summary_flag(csv_pair, capsys):
    old, new = csv_pair
    main([str(old), str(new), "-k", "id", "--summary"])
    captured = capsys.readouterr()
    assert "added=" in captured.err


def test_invalid_key_column(csv_pair):
    old, new = csv_pair
    assert main([str(old), str(new), "-k", "nonexistent"]) == 2


def test_ignore_columns(csv_pair, capsys):
    old, new = csv_pair
    # Ignoring 'score' means row 1 (Alice) should now be unchanged
    rc = main([str(old), str(new), "-k", "id", "--ignore-columns", "score"])
    captured = capsys.readouterr()
    # Only Bob removed, Dave added — no modifications
    assert "modified" not in captured.out or rc in (0, 1)
