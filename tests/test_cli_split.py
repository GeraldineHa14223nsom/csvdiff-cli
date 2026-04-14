"""Integration tests for csvdiff.cli_split."""
import csv
import pathlib
import types

import pytest

from csvdiff.cli_split import cmd_split


def _write_csv(path: pathlib.Path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


ROWS = [
    {"id": str(i), "grp": "a" if i % 2 == 0 else "b", "v": str(i * 10)}
    for i in range(1, 7)
]


@pytest.fixture()
def tmp_csv(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(p, ROWS)
    return p


def _args(file, output_dir, chunk_size=2, by_column=None):
    ns = types.SimpleNamespace(
        file=str(file),
        output_dir=str(output_dir),
        chunk_size=chunk_size,
        by_column=by_column,
    )
    return ns


def test_split_by_count_exits_zero(tmp_csv, tmp_path):
    out = tmp_path / "out"
    rc = cmd_split(_args(tmp_csv, out, chunk_size=2))
    assert rc == 0


def test_split_by_count_creates_files(tmp_csv, tmp_path):
    out = tmp_path / "out"
    cmd_split(_args(tmp_csv, out, chunk_size=2))
    files = sorted(out.glob("chunk_*.csv"))
    assert len(files) == 3


def test_split_by_column_exits_zero(tmp_csv, tmp_path):
    out = tmp_path / "out"
    rc = cmd_split(_args(tmp_csv, out, by_column="grp"))
    assert rc == 0


def test_split_by_column_creates_one_file_per_group(tmp_csv, tmp_path):
    out = tmp_path / "out"
    cmd_split(_args(tmp_csv, out, by_column="grp"))
    files = list(out.glob("chunk_*.csv"))
    assert len(files) == 2


def test_missing_file_returns_2(tmp_path):
    out = tmp_path / "out"
    rc = cmd_split(_args(tmp_path / "missing.csv", out))
    assert rc == 2


def test_unknown_column_returns_1(tmp_csv, tmp_path):
    out = tmp_path / "out"
    rc = cmd_split(_args(tmp_csv, out, by_column="nope"))
    assert rc == 1
