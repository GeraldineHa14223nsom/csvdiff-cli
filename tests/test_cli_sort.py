"""Tests for csvdiff.cli_sort."""

import csv
import io
from pathlib import Path

import pytest

from csvdiff.cli_sort import build_sort_parser, cmd_sort


CSV_CONTENT = "id,name\n3,Charlie\n1,Alice\n2,Bob\n"


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(CSV_CONTENT)
    return p


def _run(args_list, capsys=None):
    parser = build_sort_parser()
    args = parser.parse_args(args_list)
    code = args.func(args)
    return code


def test_sort_asc(csv_file, capsys):
    code = _run(["sort", str(csv_file), "-k", "id"])
    assert code == 0
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    ids = [r["id"] for r in reader]
    assert ids == ["1", "2", "3"]


def test_sort_desc(csv_file, capsys):
    code = _run(["sort", str(csv_file), "-k", "id", "-d", "desc"])
    assert code == 0
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    ids = [r["id"] for r in reader]
    assert ids == ["3", "2", "1"]


def test_sort_by_name(csv_file, capsys):
    code = _run(["sort", str(csv_file), "-k", "name"])
    assert code == 0
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    names = [r["name"] for r in reader]
    assert names == ["Alice", "Bob", "Charlie"]


def test_sort_unknown_column_returns_1(csv_file, capsys):
    code = _run(["sort", str(csv_file), "-k", "nonexistent"])
    assert code == 1
    captured = capsys.readouterr()
    assert "nonexistent" in captured.err


def test_sort_missing_file_returns_2(tmp_path, capsys):
    code = _run(["sort", str(tmp_path / "missing.csv"), "-k", "id"])
    assert code == 2
    captured = capsys.readouterr()
    assert "error" in captured.err


def test_sort_output_file(csv_file, tmp_path, capsys):
    out_file = tmp_path / "out.csv"
    code = _run(["sort", str(csv_file), "-k", "id", "-o", str(out_file)])
    assert code == 0
    rows = list(csv.DictReader(out_file.open()))
    assert [r["id"] for r in rows] == ["1", "2", "3"]


def test_sort_multiple_keys(tmp_path, capsys):
    p = tmp_path / "multi.csv"
    p.write_text("dept,id\nB,2\nA,3\nA,1\nB,1\n")
    code = _run(["sort", str(p), "-k", "dept", "-k", "id"])
    assert code == 0
    captured = capsys.readouterr()
    reader = csv.DictReader(io.StringIO(captured.out))
    pairs = [(r["dept"], r["id"]) for r in reader]
    assert pairs == [("A", "1"), ("A", "3"), ("B", "1"), ("B", "2")]
