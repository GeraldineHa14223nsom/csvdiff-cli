"""Integration tests for csvdiff.pipeline.run."""
import csv
import os
import tempfile

import pytest

from csvdiff.pipeline import run


def _write_csv(path: str, rows: list[dict]) -> None:
    if not rows:
        open(path, "w").close()
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp_pair(tmp_path):
    a = str(tmp_path / "a.csv")
    b = str(tmp_path / "b.csv")
    return a, b


ROWS_A = [
    {"id": "1", "name": "Alice", "dept": "eng"},
    {"id": "2", "name": "Bob", "dept": "hr"},
    {"id": "3", "name": "Carol", "dept": "eng"},
]

ROWS_B = [
    {"id": "1", "name": "Alice", "dept": "eng"},
    {"id": "2", "name": "Robert", "dept": "hr"},  # modified
    {"id": "4", "name": "Dave", "dept": "eng"},   # added
]


def test_run_basic(tmp_pair):
    a, b = tmp_pair
    _write_csv(a, ROWS_A)
    _write_csv(b, ROWS_B)
    result = run(a, b, keys=["id"])
    assert len(result.added) == 1
    assert len(result.removed) == 1
    assert len(result.modified) == 1


def test_run_filter_rows(tmp_pair):
    a, b = tmp_pair
    _write_csv(a, ROWS_A)
    _write_csv(b, ROWS_B)
    # Only look at eng dept — Bob's change is in hr, so no modifications expected
    result = run(a, b, keys=["id"], filter_column="dept", filter_values=["eng"])
    assert result.modified == []
    assert len(result.added) == 1  # Dave
    assert len(result.removed) == 1  # Carol


def test_run_exclude_columns(tmp_pair):
    a, b = tmp_pair
    _write_csv(a, ROWS_A)
    _write_csv(b, ROWS_B)
    # Exclude 'name' — Bob's name change should vanish
    result = run(a, b, keys=["id"], exclude_columns=["name"])
    assert result.modified == []


def test_run_exclude_rows(tmp_pair):
    a, b = tmp_pair
    _write_csv(a, ROWS_A)
    _write_csv(b, ROWS_B)
    result = run(a, b, keys=["id"], exclude_column="dept", exclude_values=["hr"])
    assert result.modified == []
