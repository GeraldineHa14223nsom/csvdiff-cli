"""Tests for csvdiff.formatter_markdown."""
import pytest

from csvdiff.core import DiffResult
from csvdiff.formatter_markdown import MarkdownOptions, format_markdown


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        added=[{"id": "3", "name": "Charlie"}],
        removed=[{"id": "1", "name": "Alice"}],
        modified=[{"id": "2", "name": "Bobby"}],
        unchanged=[{"id": "4", "name": "Diana"}],
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], modified=[], unchanged=[])


def test_format_markdown_returns_string(result):
    output = format_markdown(result)
    assert isinstance(output, str)


def test_format_markdown_contains_added_header(result):
    output = format_markdown(result)
    assert "### Added" in output


def test_format_markdown_contains_removed_header(result):
    output = format_markdown(result)
    assert "### Removed" in output


def test_format_markdown_contains_modified_header(result):
    output = format_markdown(result)
    assert "### Modified" in output


def test_format_markdown_unchanged_excluded_by_default(result):
    output = format_markdown(result)
    assert "### Unchanged" not in output


def test_format_markdown_unchanged_included_when_requested(result):
    opts = MarkdownOptions(sections=["added", "removed", "modified", "unchanged"])
    output = format_markdown(result, options=opts)
    assert "### Unchanged" in output


def test_format_markdown_contains_row_data(result):
    output = format_markdown(result)
    assert "Charlie" in output
    assert "Alice" in output
    assert "Bobby" in output


def test_format_markdown_contains_separator_row(result):
    output = format_markdown(result)
    assert "| ---" in output


def test_format_markdown_empty_result_returns_empty_string(empty_result):
    output = format_markdown(empty_result)
    assert output.strip() == ""


def test_format_markdown_no_section_headers(result):
    opts = MarkdownOptions(show_section_headers=False)
    output = format_markdown(result, options=opts)
    assert "###" not in output
    assert "|" in output


def test_format_markdown_truncates_long_values():
    long_val = "A" * 60
    res = DiffResult(
        added=[{"id": "1", "name": long_val}],
        removed=[],
        modified=[],
        unchanged=[],
    )
    opts = MarkdownOptions(max_col_width=20)
    output = format_markdown(res, options=opts)
    assert long_val not in output
    assert "…" in output


def test_format_markdown_only_selected_sections(result):
    opts = MarkdownOptions(sections=["added"])
    output = format_markdown(result, options=opts)
    assert "### Added" in output
    assert "### Removed" not in output
    assert "### Modified" not in output
