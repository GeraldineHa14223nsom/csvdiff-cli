"""Tests for csvdiff core diffing logic and output formatters."""

import json
import pytest

from csvdiff.core import diff_csv, DiffResult
from csvdiff.formatters import render


CSV_A = """id,name,score
1,Alice,90
2,Bob,85
3,Carol,78
"""

CSV_B = """id,name,score
1,Alice,95
3,Carol,78
4,Dave,88
"""


@pytest.fixture
def result() -> DiffResult:
    return diff_csv(CSV_A, CSV_B, key_columns=["id"])


def test_added_rows(result):
    assert len(result.added) == 1
    assert result.added[0]["name"] == "Dave"


def test_removed_rows(result):
    assert len(result.removed) == 1
    assert result.removed[0]["name"] == "Bob"


def test_modified_rows(result):
    assert len(result.modified) == 1
    old, new = result.modified[0]
    assert old["score"] == "90"
    assert new["score"] == "95"


def test_unchanged_rows(result):
    assert len(result.unchanged) == 1
    assert result.unchanged[0]["name"] == "Carol"


def test_has_differences(result):
    assert result.has_differences is True


def test_no_differences():
    r = diff_csv(CSV_A, CSV_A, key_columns=["id"])
    assert not r.has_differences
    assert len(r.unchanged) == 3


def test_ignore_columns():
    r = diff_csv(CSV_A, CSV_B, key_columns=["id"], ignore_columns=["score"])
    assert len(r.modified) == 0


def test_summary(result):
    s = result.summary()
    assert s == {"added": 1, "removed": 1, "modified": 1, "unchanged": 1}


def test_render_text(result):
    output = render(result, fmt="text")
    assert "ADDED" in output
    assert "REMOVED" in output
    assert "MODIFIED" in output
    assert "Summary:" in output


def test_render_json(result):
    output = render(result, fmt="json")
    data = json.loads(output)
    assert data["summary"]["added"] == 1
    assert len(data["modified"]) == 1
    assert "before" in data["modified"][0]


def test_render_csv(result):
    output = render(result, fmt="csv")
    assert "_diff" in output
    assert "added" in output
    assert "removed" in output


def test_render_unknown_format(result):
    with pytest.raises(ValueError, match="Unknown format"):
        render(result, fmt="xml")


def test_modified_row_key_matches(result):
    """Ensure the key column value is consistent between before and after in modified rows."""
    for old, new in result.modified:
        assert old["id"] == new["id"]
