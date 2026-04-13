"""Tests for csvdiff.reporter."""

from __future__ import annotations

import io
import pytest

from csvdiff.core import DiffResult
from csvdiff.reporter import ReportOptions, build_report, print_report


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        added=[{"id": "3", "name": "Charlie"}],
        removed=[{"id": "2", "name": "Bob"}],
        modified=[{"id": "1", "name": "Alice Updated"}],
        unchanged=[{"id": "0", "name": "Zero"}],
    )


def test_report_contains_counts(result: DiffResult) -> None:
    report = build_report(result, ReportOptions(color=False))
    assert "Added rows    : 1" in report
    assert "Removed rows  : 1" in report
    assert "Modified rows : 1" in report
    assert "Unchanged rows: 1" in report


def test_report_contains_change_rate(result: DiffResult) -> None:
    report = build_report(result, ReportOptions(color=False))
    assert "Change rate" in report
    assert "%" in report


def test_report_shows_sample_rows(result: DiffResult) -> None:
    opts = ReportOptions(color=False, show_sample=True, sample_size=2)
    report = build_report(result, opts)
    assert "Charlie" in report
    assert "Bob" in report
    assert "Alice Updated" in report


def test_report_hides_sample_when_disabled(result: DiffResult) -> None:
    opts = ReportOptions(color=False, show_sample=False)
    report = build_report(result, opts)
    assert "Charlie" not in report
    assert "Bob" not in report


def test_report_sample_truncation() -> None:
    many_added = [{"id": str(i)} for i in range(10)]
    result = DiffResult(added=many_added, removed=[], modified=[], unchanged=[])
    opts = ReportOptions(color=False, show_sample=True, sample_size=3)
    report = build_report(result, opts)
    assert "... and 7 more" in report


def test_report_no_color_omits_escape_codes(result: DiffResult) -> None:
    report = build_report(result, ReportOptions(color=False))
    assert "\033[" not in report


def test_report_with_color_includes_escape_codes(result: DiffResult) -> None:
    report = build_report(result, ReportOptions(color=True))
    assert "\033[" in report


def test_print_report_writes_to_file(result: DiffResult) -> None:
    buf = io.StringIO()
    print_report(result, ReportOptions(color=False), file=buf)
    output = buf.getvalue()
    assert "CSV Diff Report" in output
    assert "Added rows" in output


def test_empty_diff_report() -> None:
    result = DiffResult(added=[], removed=[], modified=[], unchanged=[])
    report = build_report(result, ReportOptions(color=False))
    assert "Added rows    : 0" in report
    assert "Change rate   : 0.0%" in report
