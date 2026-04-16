"""Anonymize CSV columns via hashing or masking."""
from __future__ import annotations
import hashlib
import re
from dataclasses import dataclass, field
from typing import List, Dict


class AnonymizerError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class AnonResult:
    headers: List[str]
    rows: List[Dict[str, str]]
    anonymized_columns: List[str]

    @property
    def row_count(self) -> int:
        return len(self.rows)


def _hash_value(value: str, salt: str = "") -> str:
    raw = (salt + value).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def _mask_value(value: str, char: str = "*", keep: int = 0) -> str:
    if keep and len(value) > keep:
        return value[:keep] + char * (len(value) - keep)
    return char * len(value)


def _validate(headers: List[str], columns: List[str]) -> None:
    missing = [c for c in columns if c not in headers]
    if missing:
        raise AnonymizerError(f"Unknown columns: {', '.join(missing)}")


def anonymize(
    rows: List[Dict[str, str]],
    columns: List[str],
    method: str = "hash",
    salt: str = "",
    mask_char: str = "*",
    keep: int = 0,
) -> AnonResult:
    if not rows:
        return AnonResult(headers=[], rows=[], anonymized_columns=columns)
    headers = list(rows[0].keys())
    _validate(headers, columns)
    if method not in ("hash", "mask"):
        raise AnonymizerError(f"Unknown method: {method!r}. Use 'hash' or 'mask'.")
    out = []
    for row in rows:
        new_row = dict(row)
        for col in columns:
            val = row.get(col, "")
            if method == "hash":
                new_row[col] = _hash_value(val, salt)
            else:
                new_row[col] = _mask_value(val, mask_char, keep)
        out.append(new_row)
    return AnonResult(headers=headers, rows=out, anonymized_columns=list(columns))
