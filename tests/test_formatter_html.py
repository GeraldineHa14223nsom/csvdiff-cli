"""Tests for csvdiff.formatter_html."""
import pytest

from csvdiff.core import DiffResult
from csvdiff.formatter_html import HtmlOptions, format_html


@pytest.fixture()
def result() -> DiffResult:
    added = [{"id": "3", "name": "Carol"}]
    removed = [{"id": "2", "name": "Bob"}]
    modified = [{"id": "1", "name": "Alice-Updated"}]
    unchanged = [{"id": "0", "name": "Zero"}]
    return DiffResult(added=added, removed=removed, modified=modified, unchanged=unchanged)


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], modified=[], unchanged=[])


def test_format_html_returns_string(result):
    html = format_html(result)
    assert isinstance(html, str)


def test_format_html_contains_doctype(result):
    html = format_html(result)
    assert html.startswith("<!DOCTYPE html>")


def test_format_html_contains_title(result):
    html = format_html(result)
    assert "CSV Diff Report" in html


def test_custom_title(result):
    opts = HtmlOptions(title="My Report")
    html = format_html(result, opts)
    assert "My Report" in html


def test_added_row_has_added_class(result):
    html = format_html(result)
    assert 'class="csvdiff-added"' in html


def test_removed_row_has_removed_class(result):
    html = format_html(result)
    assert 'class="csvdiff-removed"' in html


def test_modified_row_has_modified_class(result):
    html = format_html(result)
    assert 'class="csvdiff-modified"' in html


def test_unchanged_hidden_by_default(result):
    html = format_html(result)
    assert 'class="csvdiff-unchanged"' not in html


def test_unchanged_shown_when_enabled(result):
    opts = HtmlOptions(show_unchanged=True)
    html = format_html(result, opts)
    assert 'class="csvdiff-unchanged"' in html


def test_empty_result_shows_no_differences(empty_result):
    html = format_html(empty_result)
    assert "No differences found." in html


def test_html_escapes_special_chars():
    r = DiffResult(
        added=[{"id": "1", "name": "<Alice & Bob>"}],
        removed=[], modified=[], unchanged=[],
    )
    html = format_html(r)
    assert "&lt;Alice &amp; Bob&gt;" in html
    assert "<Alice & Bob>" not in html


def test_header_row_present(result):
    html = format_html(result)
    assert 'class="csvdiff-header"' in html
    assert "<th>id</th>" in html


def test_max_rows_limits_output():
    many = [{"id": str(i), "name": f"Row{i}"} for i in range(50)]
    r = DiffResult(added=many, removed=[], modified=[], unchanged=[])
    opts = HtmlOptions(max_rows=5)
    html = format_html(r, opts)
    assert html.count('class="csvdiff-added"') == 5
