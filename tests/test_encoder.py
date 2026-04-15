"""Tests for csvdiff.encoder."""
import pytest

from csvdiff.encoder import (
    EncoderError,
    decode_rows,
    encode_rows,
)

ROWS = [
    {"id": "1", "name": "Alice", "score": "95"},
    {"id": "2", "name": "Bob",   "score": "87"},
]


# ── encode_rows / decode_rows – JSON Lines ────────────────────────────────────

def test_encode_jsonl_produces_one_line_per_row():
    out = encode_rows(ROWS, "jsonl")
    lines = [l for l in out.splitlines() if l.strip()]
    assert len(lines) == 2


def test_encode_decode_jsonl_roundtrip():
    encoded = encode_rows(ROWS, "jsonl")
    decoded = decode_rows(encoded, "jsonl")
    assert decoded == ROWS


def test_encode_jsonl_empty_rows():
    out = encode_rows([], "jsonl")
    assert out == ""


def test_decode_jsonl_skips_blank_lines():
    text = '{"id": "1"}\n\n{"id": "2"}\n'
    rows = decode_rows(text, "jsonl")
    assert len(rows) == 2


def test_decode_jsonl_invalid_json_raises():
    with pytest.raises(EncoderError, match="Invalid JSON"):
        decode_rows("not-json\n", "jsonl")


def test_decode_jsonl_non_object_raises():
    with pytest.raises(EncoderError, match="not a JSON object"):
        decode_rows("[1, 2, 3]\n", "jsonl")


# ── encode_rows / decode_rows – TSV ──────────────────────────────────────────

def test_encode_tsv_has_header():
    out = encode_rows(ROWS, "tsv")
    first_line = out.splitlines()[0]
    assert "id" in first_line and "name" in first_line


def test_encode_tsv_uses_tab_delimiter():
    out = encode_rows(ROWS, "tsv")
    first_line = out.splitlines()[0]
    assert "\t" in first_line


def test_encode_decode_tsv_roundtrip():
    encoded = encode_rows(ROWS, "tsv")
    decoded = decode_rows(encoded, "tsv")
    assert decoded == ROWS


def test_encode_tsv_empty_rows_no_fieldnames():
    out = encode_rows([], "tsv")
    assert out == ""


def test_encode_tsv_respects_explicit_fieldnames():
    out = encode_rows(ROWS, "tsv", fieldnames=["id", "name"])
    lines = out.splitlines()
    # header only has the two requested columns
    assert lines[0] == "id\tname"


# ── unknown format ────────────────────────────────────────────────────────────

def test_encode_unknown_format_raises():
    with pytest.raises(EncoderError, match="Unknown format"):
        encode_rows(ROWS, "xml")


def test_decode_unknown_format_raises():
    with pytest.raises(EncoderError, match="Unknown format"):
        decode_rows("", "xml")


def test_encoder_error_str():
    err = EncoderError("bad format")
    assert "EncoderError" in str(err)
