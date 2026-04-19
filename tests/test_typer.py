"""Tests for csvdiff.typer."""
import pytest
from csvdiff.typer import infer_types, TyperError


@pytest.fixture
def rows():
    return [
        {"id": "1", "price": "9.99", "active": "true", "name": "Alice"},
        {"id": "2", "price": "14.50", "active": "false", "name": "Bob"},
        {"id": "3", "price": "0.01", "active": "yes", "name": "Carol"},
    ]


def test_returns_type_result(rows):
    headers = ["id", "price", "active", "name"]
    result = infer_types(rows, headers)
    assert result.headers == headers
    assert result.row_count == 3


def test_infers_integer(rows):
    result = infer_types(rows, ["id", "price", "active", "name"])
    assert result.inferred["id"] == "integer"


def test_infers_float(rows):
    result = infer_types(rows, ["id", "price", "active", "name"])
    assert result.inferred["price"] == "float"


def test_infers_boolean(rows):
    result = infer_types(rows, ["id", "price", "active", "name"])
    assert result.inferred["active"] == "boolean"


def test_infers_string(rows):
    result = infer_types(rows, ["id", "price", "active", "name"])
    assert result.inferred["name"] == "string"


def test_empty_values_infer_string():
    rows = [{"col": ""}, {"col": ""}]
    result = infer_types(rows, ["col"])
    assert result.inferred["col"] == "string"


def test_mixed_numeric_falls_back_to_string():
    rows = [{"col": "1"}, {"col": "abc"}]
    result = infer_types(rows, ["col"])
    assert result.inferred["col"] == "string"


def test_no_headers_raises():
    with pytest.raises(TyperError):
        infer_types([], [])


def test_negative_integers_inferred():
    rows = [{"val": "-3"}, {"val": "-10"}]
    result = infer_types(rows, ["val"])
    assert result.inferred["val"] == "integer"


def test_inferred_keys_match_headers(rows):
    headers = ["id", "price", "active", "name"]
    result = infer_types(rows, headers)
    assert set(result.inferred.keys()) == set(headers)
