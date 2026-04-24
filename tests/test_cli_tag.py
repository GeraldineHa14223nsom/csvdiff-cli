"""Tests for csvdiff.cli_tag."""
import csv
import io
import os
import pytest

from csvdiff.cli_tag import cmd_tag


def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def tmp_csv(tmp_path):
    rows = [
        {"id": "1", "country": "US", "score": "10"},
        {"id": "2", "country": "GB", "score": "20"},
        {"id": "3", "country": "DE", "score": "30"},
    ]
    p = tmp_path / "data.csv"
    _write_csv(str(p), rows)
    return str(p)


class _Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _args(path, **kwargs):
    defaults = dict(
        file=path,
        column="country",
        values="US,GB",
        tag_column="tag",
        match_label="match",
        no_match_label="",
        output=None,
    )
    defaults.update(kwargs)
    return _Args(**defaults)


def test_cmd_tag_exits_zero(tmp_csv, capsys):
    rc = cmd_tag(_args(tmp_csv))
    assert rc == 0


def test_cmd_tag_stdout_contains_tag_column(tmp_csv, capsys):
    cmd_tag(_args(tmp_csv))
    captured = capsys.readouterr()
    assert "tag" in captured.out


def test_cmd_tag_writes_output_file(tmp_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    cmd_tag(_args(tmp_csv, output=out))
    assert os.path.exists(out)
    with open(out, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    assert "tag" in rows[0]


def test_cmd_tag_match_label_in_output(tmp_csv, capsys):
    cmd_tag(_args(tmp_csv, match_label="yes", no_match_label="no"))
    captured = capsys.readouterr()
    assert "yes" in captured.out
    assert "no" in captured.out


def test_cmd_tag_missing_file_returns_2():
    with pytest.raises(SystemExit) as exc_info:
        cmd_tag(_args("no_such_file.csv"))
    assert exc_info.value.code == 2


def test_cmd_tag_bad_column_returns_1(tmp_csv, capsys):
    rc = cmd_tag(_args(tmp_csv, column="nonexistent"))
    assert rc == 1
