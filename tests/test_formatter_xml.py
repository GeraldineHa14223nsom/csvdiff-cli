"""Tests for csvdiff.formatter_xml."""
import pytest
from csvdiff.core import DiffResult
from csvdiff.formatter_xml import XmlOptions, format_xml


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        added=[{"id": "3", "name": "Carol"}],
        removed=[{"id": "1", "name": "Alice"}],
        modified=[
            {
                "before": {"id": "2", "name": "Bob"},
                "after": {"id": "2", "name": "Bobby"},
            }
        ],
        unchanged=[{"id": "4", "name": "Dave"}],
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], modified=[], unchanged=[])


def test_format_xml_returns_string(result):
    xml = format_xml(result)
    assert isinstance(xml, str)


def test_format_xml_contains_root_tag(result):
    xml = format_xml(result)
    assert xml.startswith("<csvdiff")


def test_format_xml_custom_title(result):
    opts = XmlOptions(title="report")
    xml = format_xml(result, opts)
    assert xml.startswith("<report")


def test_format_xml_added_count(result):
    xml = format_xml(result)
    assert 'count="1"' in xml


def test_format_xml_added_row_value(result):
    xml = format_xml(result)
    assert "Carol" in xml


def test_format_xml_removed_row_value(result):
    xml = format_xml(result)
    assert "Alice" in xml


def test_format_xml_modified_before_after(result):
    xml = format_xml(result)
    assert "<before>" in xml
    assert "<after>" in xml


def test_format_xml_modified_values(result):
    xml = format_xml(result)
    assert "Bobby" in xml
    assert "Bob" in xml


def test_format_xml_empty_result(empty_result):
    xml = format_xml(empty_result)
    assert 'count="0"' in xml


def test_format_xml_max_rows_limits_output():
    many_rows = [{"id": str(i), "name": f"Name{i}"} for i in range(50)]
    result = DiffResult(added=many_rows, removed=[], modified=[], unchanged=[])
    opts = XmlOptions(max_rows=5)
    xml = format_xml(result, opts)
    assert xml.count("<row>") == 5


def test_format_xml_truncates_long_values():
    long_val = "x" * 300
    result = DiffResult(
        added=[{"id": "1", "name": long_val}],
        removed=[],
        modified=[],
        unchanged=[],
    )
    xml = format_xml(result)
    assert "x" * 300 not in xml
    assert "..." in xml
