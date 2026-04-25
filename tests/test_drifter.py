"""Tests for csvdiff.drifter and csvdiff.cli_drift."""
from __future__ import annotations

import csv
import io
import json
import os
import types

import pytest

from csvdiff.drifter import DrifterError, DriftResult, detect_drift
from csvdiff.cli_drift import cmd_drift


# ---------------------------------------------------------------------------
# detect_drift unit tests
# ---------------------------------------------------------------------------

def test_no_drift_identical_headers():
    result = detect_drift(["id", "name", "score"], ["id", "name", "score"])
    assert result.has_drift is False
    assert result.added == []
    assert result.removed == []
    assert result.reordered is False


def test_added_column_detected():
    result = detect_drift(["id", "name"], ["id", "name", "email"])
    assert result.has_drift is True
    assert result.added == ["email"]
    assert result.removed == []


def test_removed_column_detected():
    result = detect_drift(["id", "name", "email"], ["id", "name"])
    assert result.has_drift is True
    assert result.removed == ["email"]
    assert result.added == []


def test_reordered_columns_detected():
    result = detect_drift(["id", "name", "score"], ["id", "score", "name"])
    assert result.has_drift is True
    assert result.reordered is True
    assert result.added == []
    assert result.removed == []


def test_added_and_removed_simultaneously():
    result = detect_drift(["id", "name"], ["id", "email"])
    assert result.added == ["email"]
    assert result.removed == ["name"]
    assert result.has_drift is True


def test_column_counts():
    result = detect_drift(["a", "b", "c"], ["a", "b"])
    assert result.column_count_left == 3
    assert result.column_count_right == 2


def test_empty_left_raises():
    with pytest.raises(DrifterError):
        detect_drift([], ["id"])


def test_empty_right_raises():
    with pytest.raises(DrifterError):
        detect_drift(["id"], [])


# ---------------------------------------------------------------------------
# cmd_drift integration tests
# ---------------------------------------------------------------------------

def _write_csv(tmp_path, filename: str, headers: list) -> str:
    path = os.path.join(str(tmp_path), filename)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
    return path


def _args(left, right, fmt="text"):
    return types.SimpleNamespace(left=left, right=right, format=fmt)


def test_cmd_drift_no_drift_exits_zero(tmp_path):
    left = _write_csv(tmp_path, "l.csv", ["id", "name"])
    right = _write_csv(tmp_path, "r.csv", ["id", "name"])
    assert cmd_drift(_args(left, right)) == 0


def test_cmd_drift_with_drift_exits_one(tmp_path):
    left = _write_csv(tmp_path, "l.csv", ["id", "name"])
    right = _write_csv(tmp_path, "r.csv", ["id", "name", "score"])
    assert cmd_drift(_args(left, right)) == 1


def test_cmd_drift_json_output(tmp_path, capsys):
    left = _write_csv(tmp_path, "l.csv", ["id", "name"])
    right = _write_csv(tmp_path, "r.csv", ["id", "email"])
    code = cmd_drift(_args(left, right, fmt="json"))
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["has_drift"] is True
    assert "email" in payload["added"]
    assert "name" in payload["removed"]
    assert code == 1


def test_cmd_drift_text_output(tmp_path, capsys):
    left = _write_csv(tmp_path, "l.csv", ["id", "name"])
    right = _write_csv(tmp_path, "r.csv", ["id", "name"])
    cmd_drift(_args(left, right, fmt="text"))
    captured = capsys.readouterr()
    assert "Schema drift detected" in captured.out
