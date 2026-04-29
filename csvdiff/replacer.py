"""Replace cell values in CSV rows based on column/pattern rules."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class ReplacerError(Exception):
    def __str__(self) -> str:
        return f"ReplacerError: {self.args[0]}"


@dataclass
class ReplaceResult:
    rows: List[Dict[str, str]]
    headers: List[str]
    replaced_count: int
    column: str

    @property
    def row_count(self) -> int:
        return len(self.rows)


def _validate(rows: List[Dict[str, str]], column: str) -> None:
    if not rows:
        return
    if column not in rows[0]:
        raise ReplacerError(f"Column '{column}' not found in headers")


def replace_values(
    rows: List[Dict[str, str]],
    column: str,
    pattern: str,
    replacement: str,
    regex: bool = False,
    case_sensitive: bool = True,
) -> ReplaceResult:
    """Replace values in *column* matching *pattern* with *replacement*.

    Args:
        rows: Input rows as list of dicts.
        column: Column name to operate on.
        pattern: The string or regex pattern to match.
        replacement: Value to substitute.
        regex: When True, treat *pattern* as a regular expression.
        case_sensitive: When False, match ignoring case (regex mode only).

    Returns:
        ReplaceResult with updated rows and replacement count.
    """
    _validate(rows, column)
    headers = list(rows[0].keys()) if rows else []
    out: List[Dict[str, str]] = []
    replaced_count = 0

    flags = 0 if case_sensitive else re.IGNORECASE

    for row in rows:
        new_row = dict(row)
        original = row[column]
        if regex:
            new_val, n = re.subn(pattern, replacement, original, flags=flags)
        else:
            if case_sensitive:
                new_val = original.replace(pattern, replacement)
                n = 0 if new_val == original else 1
            else:
                new_val = re.sub(
                    re.escape(pattern), replacement, original, flags=re.IGNORECASE
                )
                n = 0 if new_val == original else 1
        if n:
            replaced_count += 1
        new_row[column] = new_val
        out.append(new_row)

    return ReplaceResult(
        rows=out,
        headers=headers,
        replaced_count=replaced_count,
        column=column,
    )
