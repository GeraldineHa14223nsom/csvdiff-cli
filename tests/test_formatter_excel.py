"""Tests for csvdiff.formatter_excel."""
from __future__ import annotations

import pytest

from csvdiff.core import DiffResult
from csvdiff.formatter_excel import (
    ExcelOptions,
    _truncate,
    _row_to_cells,
    format_excel_csv,
)


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        added=[{"id": "3", "name": "Carol"}],
        removed=[{"id": "2", "name": "Bob"}],
        modified={"1": ({"id": "1", "name": "Alice"}, {"id": "1", "name": "Alicia"})},
        unchanged=[{"id": "4", "name": "Dave"}],
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], modified={}, unchanged=[])


def test_truncate_short_string():
    assert _truncate("hello", 10) == "hello"


def test_truncate_long_string():
    result = _truncate("hello world", 8)
    assert len(result) == 8
    assert result.endswith("…")


def test_truncate_exact_length():
    assert _truncate("hello", 5) == "hello"


def test_row_to_cells_basic():
    row = {"id": "1", "name": "Alice"}
    cells = _row_to_cells(row, ["id", "name"], 64)
    assert cells == ["1", "Alice"]


def test_row_to_cells_missing_key():
    row = {"id": "1"}
    cells = _row_to_cells(row, ["id", "name"], 64)
    assert cells == ["1", ""]


def test_format_excel_csv_returns_string(result):
    out = format_excel_csv(result)
    assert isinstance(out, str)


def test_format_excel_csv_contains_added_header(result):
    out = format_excel_csv(result)
    assert "## Added" in out


def test_format_excel_csv_contains_removed_header(result):
    out = format_excel_csv(result)
    assert "## Removed" in out


def test_format_excel_csv_contains_modified_header(result):
    out = format_excel_csv(result)
    assert "## Modified" in out


def test_format_excel_csv_no_unchanged_by_default(result):
    out = format_excel_csv(result)
    assert "## Unchanged" not in out


def test_format_excel_csv_includes_unchanged_when_opt(result):
    opts = ExcelOptions(include_unchanged=True)
    out = format_excel_csv(result, opts)
    assert "## Unchanged" in out
    assert "Dave" in out


def test_format_excel_csv_added_row_present(result):
    out = format_excel_csv(result)
    assert "Carol" in out


def test_format_excel_csv_removed_row_present(result):
    out = format_excel_csv(result)
    assert "Bob" in out


def test_format_excel_csv_empty_result_is_empty(empty_result):
    out = format_excel_csv(empty_result)
    assert out.strip() == ""


def test_format_excel_csv_custom_label(result):
    opts = ExcelOptions(sheet_label_added="NEW ROWS")
    out = format_excel_csv(result, opts)
    assert "## NEW ROWS" in out
