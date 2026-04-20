"""Tests for csvdiff.differ."""
import pytest
from csvdiff.differ import (
    CellDiff,
    DifferError,
    DifferResult,
    RowDiff,
    diff_modified,
)


MODIFIED = [
    {
        "old": {"id": "1", "name": "Alice", "score": "80"},
        "new": {"id": "1", "name": "Alicia", "score": "95"},
    },
    {
        "old": {"id": "2", "name": "Bob", "score": "70"},
        "new": {"id": "2", "name": "Bob", "score": "70"},
    },
]


def test_diff_modified_returns_differ_result():
    result = diff_modified(MODIFIED, key_columns=["id"])
    assert isinstance(result, DifferResult)


def test_diff_modified_row_count():
    result = diff_modified(MODIFIED, key_columns=["id"])
    assert len(result.rows) == 2


def test_diff_modified_key_uses_key_columns():
    result = diff_modified(MODIFIED, key_columns=["id"])
    assert result.rows[0].key == "1"
    assert result.rows[1].key == "2"


def test_diff_modified_changed_columns_detected():
    result = diff_modified(MODIFIED, key_columns=["id"])
    changed = result.rows[0].changed_columns
    assert "name" in changed
    assert "score" in changed
    assert "id" not in changed


def test_diff_modified_unchanged_row_has_no_changes():
    result = diff_modified(MODIFIED, key_columns=["id"])
    assert result.rows[1].change_count == 0


def test_total_changed_cells():
    result = diff_modified(MODIFIED, key_columns=["id"])
    # row 0 has 2 changed cells; row 1 has 0
    assert result.total_changed_cells == 2


def test_cell_diff_is_changed_true():
    cell = CellDiff(column="name", old_value="Alice", new_value="Alicia", opcodes=[])
    assert cell.is_changed is True


def test_cell_diff_is_changed_false():
    cell = CellDiff(column="id", old_value="1", new_value="1", opcodes=[])
    assert cell.is_changed is False


def test_cell_diff_ratio_identical():
    cell = CellDiff(column="id", old_value="hello", new_value="hello", opcodes=[])
    assert cell.ratio == pytest.approx(1.0)


def test_cell_diff_ratio_different():
    cell = CellDiff(column="name", old_value="Alice", new_value="Alicia", opcodes=[])
    assert 0.0 < cell.ratio < 1.0


def test_diff_modified_no_key_columns_uses_first_value():
    result = diff_modified(MODIFIED)
    assert result.rows[0].key == "1"


def test_diff_modified_invalid_input_raises():
    with pytest.raises(DifferError):
        diff_modified("not a list")


def test_diff_modified_missing_old_key_raises():
    with pytest.raises(DifferError):
        diff_modified([{"new": {"id": "1"}}])


def test_diff_modified_missing_new_key_raises():
    with pytest.raises(DifferError):
        diff_modified([{"old": {"id": "1"}}])


def test_row_diff_change_count():
    row = RowDiff(key="1", cells=[
        CellDiff("a", "x", "y", []),
        CellDiff("b", "z", "z", []),
    ])
    assert row.change_count == 1


def test_opcodes_populated():
    result = diff_modified(MODIFIED, key_columns=["id"])
    name_cell = next(c for c in result.rows[0].cells if c.column == "name")
    assert len(name_cell.opcodes) > 0
