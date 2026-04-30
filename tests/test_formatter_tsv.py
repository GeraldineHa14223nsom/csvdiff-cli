"""Tests for csvdiff.formatter_tsv."""
import pytest

from csvdiff.core import DiffResult
from csvdiff.formatter_tsv import (
    TsvOptions,
    _truncate,
    _tsv_row,
    format_tsv,
)


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        added=[{"id": "3", "name": "Carol"}],
        removed=[{"id": "2", "name": "Bob"}],
        modified=[{"key": "1", "old": {"id": "1", "name": "Alice"}, "new": {"id": "1", "name": "Alicia"}}],
        unchanged=[{"id": "4", "name": "Dave"}],
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], modified=[], unchanged=[])


def test_truncate_short_string():
    assert _truncate("hello", 10) == "hello"


def test_truncate_long_string():
    result = _truncate("hello world", 8)
    assert result == "hello..."
    assert len(result) == 8


def test_truncate_exact_length():
    assert _truncate("hello", 5) == "hello"


def test_tsv_row_uses_tabs():
    row = {"id": "1", "name": "Alice"}
    line = _tsv_row(row, ["id", "name"], 60)
    assert "\t" in line
    assert line == "1\tAlice"


def test_tsv_row_missing_key_empty_string():
    row = {"id": "1"}
    line = _tsv_row(row, ["id", "name"], 60)
    assert line == "1\t"


def test_format_tsv_returns_string(result):
    output = format_tsv(result)
    assert isinstance(output, str)


def test_format_tsv_empty_result_returns_empty(empty_result):
    output = format_tsv(empty_result)
    assert output == ""


def test_format_tsv_contains_added_header(result):
    output = format_tsv(result)
    assert "# ADDED" in output


def test_format_tsv_contains_removed_header(result):
    output = format_tsv(result)
    assert "# REMOVED" in output


def test_format_tsv_contains_modified_header(result):
    output = format_tsv(result)
    assert "# MODIFIED" in output


def test_format_tsv_contains_unchanged_header(result):
    output = format_tsv(result)
    assert "# UNCHANGED" in output


def test_format_tsv_added_row_present(result):
    output = format_tsv(result)
    assert "Carol" in output


def test_format_tsv_removed_row_present(result):
    output = format_tsv(result)
    assert "Bob" in output


def test_format_tsv_modified_new_value_present(result):
    output = format_tsv(result)
    assert "Alicia" in output


def test_format_tsv_no_section_headers_when_disabled(result):
    opts = TsvOptions(include_section_headers=False)
    output = format_tsv(result, opts)
    assert "# ADDED" not in output
    assert "# REMOVED" not in output


def test_format_tsv_custom_title(result):
    opts = TsvOptions(title="My Report")
    output = format_tsv(result, opts)
    assert "My Report" in output


def test_format_tsv_cells_separated_by_tab(result):
    output = format_tsv(result)
    data_lines = [l for l in output.splitlines() if l and not l.startswith("#")]
    assert any("\t" in line for line in data_lines)


def test_format_tsv_max_cell_width_truncates(result):
    opts = TsvOptions(max_cell_width=3)
    output = format_tsv(result, opts)
    for line in output.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        for cell in line.split("\t"):
            assert len(cell) <= 3
