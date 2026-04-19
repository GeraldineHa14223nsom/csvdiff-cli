"""Infer or assert column data types from CSV rows."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


class TyperError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class TypeResult:
    headers: List[str]
    rows: List[Dict[str, str]]
    inferred: Dict[str, str]

    @property
    def row_count(self) -> int:
        return len(self.rows)


_CHECKS = [
    ("integer", lambda v: v.lstrip("-").isdigit()),
    ("float", _is_float),
    ("boolean", lambda v: v.lower() in {"true", "false", "1", "0", "yes", "no"}),
    ("string", lambda v: True),
]


def _is_float(v: str) -> bool:
    try:
        float(v)
        return True
    except ValueError:
        return False


_CHECKS = [
    ("integer", lambda v: v.lstrip("-").isdigit()),
    ("float", _is_float),
    ("boolean", lambda v: v.lower() in {"true", "false", "1", "0", "yes", "no"}),
    ("string", lambda v: True),
]


def _infer_type(values: List[str]) -> str:
    non_empty = [v.strip() for v in values if v.strip() != ""]
    if not non_empty:
        return "string"
    for name, check in _CHECKS:
        if all(check(v) for v in non_empty):
            return name
    return "string"


def infer_types(rows: List[Dict[str, str]], headers: List[str]) -> TypeResult:
    if not headers:
        raise TyperError("No headers provided for type inference.")
    inferred: Dict[str, str] = {}
    for col in headers:
        values = [row.get(col, "") for row in rows]
        inferred[col] = _infer_type(values)
    return TypeResult(headers=headers, rows=rows, inferred=inferred)
