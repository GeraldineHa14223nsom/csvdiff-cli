"""Tests for the LaTeX formatter."""
from __future__ import annotations

import pytest

from csvdiff.core import DiffResult
from csvdiff.formatter_latex import (
    LatexOptions,
    _escape,
    _truncate,
    format_latex,
)


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        added=[{"id": "3", "name": "Charlie"}],
        removed=[{"id": "2", "name": "Bob"}],
        modified=[
            {
                "key": {"id": "1"},
                "old": {"id": "1", "name": "Alice"},
                "new": {"id": "1", "name": "Alicia"},
            }
        ],
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


def test_escape_ampersand():
    assert _escape("a & b") == "a \\& b"


def test_escape_underscore():
    assert _escape("col_name") == "col\\_name"


def test_escape_percent():
    assert _escape("50%") == "50\\%"


def test_escape_dollar():
    assert _escape("$100") == "\\$100"


def test_format_latex_returns_string(result):
    out = format_latex(result)
    assert isinstance(out, str)


def test_format_latex_contains_title(result):
    out = format_latex(result, LatexOptions(title="My Report"))
    assert "My Report" in out


def test_format_latex_contains_added_section(result):
    out = format_latex(result)
    assert "Added Rows" in out


def test_format_latex_contains_removed_section(result):
    out = format_latex(result)
    assert "Removed Rows" in out


def test_format_latex_contains_modified_section(result):
    out = format_latex(result)
    assert "Modified Rows" in out


def test_format_latex_contains_tabular(result):
    out = format_latex(result)
    assert "\\begin{tabular}" in out
    assert "\\end{tabular}" in out


def test_format_latex_contains_added_row_value(result):
    out = format_latex(result)
    assert "Charlie" in out


def test_format_latex_unchanged_hidden_by_default(result):
    out = format_latex(result)
    assert "Unchanged Rows" not in out


def test_format_latex_show_unchanged(result):
    opts = LatexOptions(show_unchanged=True)
    out = format_latex(result, opts)
    assert "Unchanged Rows" in out
    assert "Dave" in out


def test_format_latex_empty_result_no_tabular(empty_result):
    out = format_latex(empty_result)
    assert "\\begin{tabular}" not in out
