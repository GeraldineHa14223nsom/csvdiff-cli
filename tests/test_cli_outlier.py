"""Tests for csvdiff.cli_outlier."""
import csv
import io
import pytest
from csvdiff.cli_outlier import cmd_outlier, _render_text
from csvdiff.outlier import detect_outliers


def _write_csv(tmp_path, rows, name="data.csv"):
    p = tmp_path / name
    if not rows:
        p.write_text("")
        return str(p)
    fieldnames = list(rows[0].keys())
    with open(str(p), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    return str(p)


class _Args:
    def __init__(self, file, column, method="zscore", threshold=3.0, fmt="text"):
        self.file = file
        self.column = column
        self.method = method
        self.threshold = threshold
        self.format = fmt


def _rows(tmp_path):
    data = [{"id": str(i), "val": str(v)} for i, v in enumerate([10, 10, 10, 10, 10, 1000])]
    return _write_csv(tmp_path, data)


def test_cmd_outlier_exits_zero(tmp_path):
    path = _rows(tmp_path)
    assert cmd_outlier(_Args(path, "val")) == 0


def test_cmd_outlier_json_exits_zero(tmp_path, capsys):
    path = _rows(tmp_path)
    code = cmd_outlier(_Args(path, "val", fmt="json"))
    assert code == 0
    import json
    out = json.loads(capsys.readouterr().out)
    assert "outlier_count" in out


def test_cmd_outlier_missing_file_returns_2(tmp_path):
    code = cmd_outlier(_Args(str(tmp_path / "nope.csv"), "val"))
    assert code == 2


def test_cmd_outlier_bad_column_returns_1(tmp_path):
    path = _rows(tmp_path)
    code = cmd_outlier(_Args(path, "nonexistent"))
    assert code == 1


def test_render_text_contains_outlier_count(tmp_path):
    data = [{"val": str(v)} for v in [10, 10, 10, 10, 10, 1000]]
    result = detect_outliers(data, "val", method="zscore", threshold=2.0)
    text = _render_text(result)
    assert "Outliers" in text
    assert "1" in text


def test_cmd_outlier_iqr_method(tmp_path):
    path = _rows(tmp_path)
    code = cmd_outlier(_Args(path, "val", method="iqr", threshold=1.5))
    assert code == 0
