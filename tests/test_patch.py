"""Tests for csvdiff.patch — patch generation and application."""

from __future__ import annotations

import io
import json

import pytest

from csvdiff.core import DiffResult
from csvdiff.patch import apply_patch, load_patch, to_patch, write_patch


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        added=[{"id": "3", "name": "Carol"}],
        removed=[{"id": "2", "name": "Bob"}],
        modified=[
            {
                "key": {"id": "1"},
                "before": {"id": "1", "name": "Alice"},
                "after": {"id": "1", "name": "Alicia"},
            }
        ],
        unchanged=[],
    )


def test_to_patch_keys(result: DiffResult) -> None:
    patch = to_patch(result, keys=["id"])
    assert patch["keys"] == ["id"]


def test_to_patch_added(result: DiffResult) -> None:
    patch = to_patch(result, keys=["id"])
    assert patch["added"] == [{"id": "3", "name": "Carol"}]


def test_to_patch_removed(result: DiffResult) -> None:
    patch = to_patch(result, keys=["id"])
    assert patch["removed"] == [{"id": "2", "name": "Bob"}]


def test_to_patch_modified_structure(result: DiffResult) -> None:
    patch = to_patch(result, keys=["id"])
    mod = patch["modified"][0]
    assert "key" in mod and "before" in mod and "after" in mod


def test_write_and_load_patch_roundtrip(result: DiffResult) -> None:
    buf = io.StringIO()
    write_patch(result, keys=["id"], fp=buf)
    buf.seek(0)
    loaded = load_patch(buf)
    assert loaded["keys"] == ["id"]
    assert len(loaded["added"]) == 1


def test_write_patch_valid_json(result: DiffResult) -> None:
    buf = io.StringIO()
    write_patch(result, keys=["id"], fp=buf)
    buf.seek(0)
    data = json.loads(buf.read())
    assert isinstance(data, dict)


def test_apply_patch_addition() -> None:
    rows = [{"id": "1", "name": "Alice"}]
    patch = {"keys": ["id"], "added": [{"id": "2", "name": "Bob"}], "removed": [], "modified": []}
    result = apply_patch(rows, patch)
    ids = {r["id"] for r in result}
    assert "2" in ids


def test_apply_patch_removal() -> None:
    rows = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    patch = {"keys": ["id"], "added": [], "removed": [{"id": "2", "name": "Bob"}], "modified": []}
    result = apply_patch(rows, patch)
    assert all(r["id"] != "2" for r in result)


def test_apply_patch_modification() -> None:
    rows = [{"id": "1", "name": "Alice"}]
    patch = {
        "keys": ["id"],
        "added": [],
        "removed": [],
        "modified": [{"key": {"id": "1"}, "before": {"id": "1", "name": "Alice"}, "after": {"id": "1", "name": "Alicia"}}],
    }
    result = apply_patch(rows, patch)
    assert result[0]["name"] == "Alicia"


def test_apply_patch_unknown_removal_is_noop() -> None:
    rows = [{"id": "1", "name": "Alice"}]
    patch = {"keys": ["id"], "added": [], "removed": [{"id": "99", "name": "Ghost"}], "modified": []}
    result = apply_patch(rows, patch)
    assert len(result) == 1
