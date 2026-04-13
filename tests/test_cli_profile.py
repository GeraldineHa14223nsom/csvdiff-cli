"""Tests for csvdiff.cli_profile."""
import csv
import io
import json
import os
import tempfile

import pytest

from csvdiff.cli_profile import cmd_profile, _render_text, _render_json
from csvdiff.profiler import profile_rows


def _write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def tmp_csv(tmp_path):
    rows = [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob",   "score": ""},
    ]
    p = tmp_path / "data.csv"
    _write_csv(rows, str(p))
    return str(p)


class _Args:
    def __init__(self, file, fmt="text", sample_size=5):
        self.file = file
        self.format = fmt
        self.sample_size = sample_size


def test_cmd_profile_text_exit_zero(tmp_csv):
    assert cmd_profile(_Args(tmp_csv)) == 0


def test_cmd_profile_json_exit_zero(tmp_csv):
    assert cmd_profile(_Args(tmp_csv, fmt="json")) == 0


def test_cmd_profile_missing_file_returns_2():
    assert cmd_profile(_Args("/no/such/file.csv")) == 2


def test_render_text_contains_column_name():
    rows = [{"city": "Paris", "pop": "2M"}]
    result = profile_rows(rows)
    text = _render_text(result)
    assert "city" in text
    assert "pop" in text


def test_render_json_is_valid_json():
    rows = [{"a": "1"}, {"a": "2"}]
    result = profile_rows(rows)
    data = json.loads(_render_json(result))
    assert isinstance(data, list)
    assert data[0]["column"] == "a"


def test_render_json_fill_rate_present():
    rows = [{"x": "hi"}, {"x": ""}]
    result = profile_rows(rows)
    data = json.loads(_render_json(result))
    assert "fill_rate" in data[0]
    assert data[0]["fill_rate"] == pytest.approx(0.5)


def test_render_text_shows_fill_rate(tmp_csv):
    rows = [{"id": "1", "name": "Alice", "score": "90"},
            {"id": "2", "name": "Bob",   "score": ""}]
    result = profile_rows(rows)
    text = _render_text(result)
    assert "fill_rate" in text
