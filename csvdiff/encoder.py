"""Encode/decode CSV rows to and from common formats (JSON lines, TSV)."""
from __future__ import annotations

import csv
import io
import json
from typing import Iterable, Iterator, List


class EncoderError(Exception):
    def __str__(self) -> str:
        return f"EncoderError: {self.args[0]}"


SUPPORTED_FORMATS = ("jsonl", "tsv")


def _validate_format(fmt: str) -> None:
    if fmt not in SUPPORTED_FORMATS:
        raise EncoderError(
            f"Unknown format {fmt!r}. Supported: {', '.join(SUPPORTED_FORMATS)}"
        )


def encode_rows(
    rows: Iterable[dict],
    fmt: str,
    fieldnames: List[str] | None = None,
) -> str:
    """Encode an iterable of row dicts to a string in *fmt* format."""
    _validate_format(fmt)
    rows = list(rows)
    if fmt == "jsonl":
        return _encode_jsonl(rows)
    if fmt == "tsv":
        return _encode_tsv(rows, fieldnames)
    raise EncoderError(f"Unhandled format: {fmt!r}")


def decode_rows(text: str, fmt: str) -> List[dict]:
    """Decode a string in *fmt* format to a list of row dicts."""
    _validate_format(fmt)
    if fmt == "jsonl":
        return _decode_jsonl(text)
    if fmt == "tsv":
        return _decode_tsv(text)
    raise EncoderError(f"Unhandled format: {fmt!r}")


# ── JSON Lines ────────────────────────────────────────────────────────────────

def _encode_jsonl(rows: List[dict]) -> str:
    lines = [json.dumps(row, ensure_ascii=False) for row in rows]
    return "\n".join(lines) + ("\n" if lines else "")


def _decode_jsonl(text: str) -> List[dict]:
    rows: List[dict] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EncoderError(f"Invalid JSON on line {lineno}: {exc}") from exc
        if not isinstance(obj, dict):
            raise EncoderError(f"Line {lineno} is not a JSON object")
        rows.append(obj)
    return rows


# ── TSV ───────────────────────────────────────────────────────────────────────

def _encode_tsv(rows: List[dict], fieldnames: List[str] | None) -> str:
    if not rows and not fieldnames:
        return ""
    fields = fieldnames or list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, delimiter="\t",
                            lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def _decode_tsv(text: str) -> List[dict]:
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    return [dict(row) for row in reader]
