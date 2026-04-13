"""Integration tests for csvdiff.cli_join."""
import csv
import io
import os

import pytest

from csvdiff.cli_join import cmd_join


def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp_pair(tmp_path):
    left = tmp_path / "left.csv"
    right = tmp_path / "right.csv"
    _write_csv(left, [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}])
    _write_csv(right, [{"id": "1", "score": "99"}, {"id": "3", "score": "55"}])
    return str(left), str(right)


class _Args:
    def __init__(self, left, right, key, how="inner", output=None,
                 include_left_only=False, include_right_only=False):
        self.left = left
        self.right = right
        self.key = key
        self.how = how
        self.output = output
        self.include_left_only = include_left_only
        self.include_right_only = include_right_only


def test_inner_join_exits_zero(tmp_pair):
    left, right = tmp_pair
    assert cmd_join(_Args(left, right, key="id")) == 0


def test_inner_join_writes_output(tmp_pair, tmp_path):
    left, right = tmp_pair
    out = str(tmp_path / "out.csv")
    cmd_join(_Args(left, right, key="id", output=out))
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 1
    assert rows[0]["id"] == "1"


def test_left_join_appends_left_only(tmp_pair, tmp_path):
    left, right = tmp_pair
    out = str(tmp_path / "out.csv")
    cmd_join(_Args(left, right, key="id", how="left",
                   output=out, include_left_only=True))
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    ids = {r["id"] for r in rows}
    assert "2" in ids


def test_missing_file_returns_2(tmp_path):
    result = cmd_join(_Args("no_such.csv", "no_such2.csv", key="id"))
    assert result == 2


def test_bad_key_returns_1(tmp_pair):
    left, right = tmp_pair
    result = cmd_join(_Args(left, right, key="nonexistent"))
    assert result == 1
