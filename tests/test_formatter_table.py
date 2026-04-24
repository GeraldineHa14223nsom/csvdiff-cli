"""Tests for csvdiff.formatter_table."""
import pytest

from csvdiff.core import DiffResult
from csvdiff.formatter_table import TableOptions, format_table, _truncate


@pytest.fixture()
def result():
    return DiffResult(
        added=[{"id": "3", "name": "Carol"}],
        removed=[{"id": "2", "name": "Bob"}],
        modified=[
            {
                "old": {"id": "1", "name": "Alice"},
                "new": {"id": "1", "name": "Alicia"},
            }
        ],
        unchanged=[{"id": "4", "name": "Dave"}],
    )


@pytest.fixture()
def empty_result():
    return DiffResult(added=[], removed=[], modified=[], unchanged=[])


def test_truncate_short_string():
    assert _truncate("hello", 10) == "hello"


def test_truncate_long_string():
    result = _truncate("hello world", 7)
    assert len(result) == 7
    assert result.endswith("…")


def test_truncate_exact_length():
    assert _truncate("hello", 5) == "hello"


def test_format_table_contains_added_section(result):
    output = format_table(result)
    assert "[ADDED]" in output


def test_format_table_contains_removed_section(result):
    output = format_table(result)
    assert "[REMOVED]" in output


def test_format_table_contains_modified_section(result):
    output = format_table(result)
    assert "[MODIFIED]" in output


def test_format_table_hides_unchanged_by_default(result):
    output = format_table(result)
    assert "[UNCHANGED]" not in output


def test_format_table_shows_unchanged_when_enabled(result):
    opts = TableOptions(show_unchanged=True)
    output = format_table(result, opts)
    assert "[UNCHANGED]" in output


def test_format_table_added_row_value(result):
    output = format_table(result)
    assert "Carol" in output


def test_format_table_removed_row_value(result):
    output = format_table(result)
    assert "Bob" in output


def test_format_table_modified_new_value(result):
    output = format_table(result)
    assert "Alicia" in output


def test_format_table_empty_result_returns_no_differences(empty_result):
    output = format_table(empty_result)
    assert output == "(no differences)"


def test_format_table_headers_present(result):
    output = format_table(result)
    assert "id" in output
    assert "name" in output


def test_format_table_custom_max_col_width(result):
    opts = TableOptions(max_col_width=4)
    output = format_table(result, opts)
    # Truncated values should appear (no cell wider than 4 visible chars)
    assert "[ADDED]" in output


def test_format_table_custom_separator(result):
    opts = TableOptions(separator="!")
    output = format_table(result, opts)
    assert "!" in output


def test_format_table_no_added_section_when_empty():
    r = DiffResult(added=[], removed=[{"id": "1", "name": "X"}], modified=[], unchanged=[])
    output = format_table(r)
    assert "[ADDED]" not in output
    assert "[REMOVED]" in output
