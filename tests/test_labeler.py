"""Tests for csvdiff.labeler."""
import pytest
from csvdiff.labeler import LabelerError, LabelResult, label_rows


@pytest.fixture()
def rows():
    return [
        {"id": "1", "dept": "eng", "name": "Alice"},
        {"id": "2", "dept": "hr", "name": "Bob"},
        {"id": "3", "dept": "eng", "name": "Carol"},
        {"id": "4", "dept": "finance", "name": "Dave"},
        {"id": "5", "dept": "hr", "name": "Eve"},
    ]


def test_returns_label_result(rows):
    result = label_rows(rows, group_column="dept")
    assert isinstance(result, LabelResult)


def test_row_count_unchanged(rows):
    result = label_rows(rows, group_column="dept")
    assert result.row_count == len(rows)


def test_label_column_added(rows):
    result = label_rows(rows, group_column="dept")
    for row in result.rows:
        assert "label" in row


def test_custom_label_column(rows):
    result = label_rows(rows, group_column="dept", label_column="group_id")
    for row in result.rows:
        assert "group_id" in row
    assert result.label_column == "group_id"


def test_auto_labels_are_numeric_strings(rows):
    result = label_rows(rows, group_column="dept")
    for row in result.rows:
        assert row["label"].isdigit()


def test_same_group_gets_same_label(rows):
    result = label_rows(rows, group_column="dept")
    labels = {row["dept"]: row["label"] for row in result.rows}
    eng_rows = [r for r in result.rows if r["dept"] == "eng"]
    assert eng_rows[0]["label"] == eng_rows[1]["label"]


def test_group_count(rows):
    result = label_rows(rows, group_column="dept")
    assert result.group_count == 3  # eng, hr, finance


def test_label_map_keys(rows):
    result = label_rows(rows, group_column="dept")
    assert set(result.label_map.keys()) == {"eng", "hr", "finance"}


def test_custom_mapping_applied(rows):
    mapping = {"eng": "engineering", "hr": "human_resources", "finance": "finance"}
    result = label_rows(rows, group_column="dept", mapping=mapping)
    alice = next(r for r in result.rows if r["name"] == "Alice")
    assert alice["label"] == "engineering"


def test_missing_mapping_key_uses_default(rows):
    mapping = {"eng": "engineering"}
    result = label_rows(rows, group_column="dept", mapping=mapping, default="other")
    bob = next(r for r in result.rows if r["name"] == "Bob")
    assert bob["label"] == "other"


def test_unknown_group_column_raises(rows):
    with pytest.raises(LabelerError):
        label_rows(rows, group_column="nonexistent")


def test_empty_rows_returns_empty_result():
    result = label_rows([], group_column="dept")
    assert result.row_count == 0
    assert result.group_count == 0
