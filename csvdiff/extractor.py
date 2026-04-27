"""Extract a subset of rows from a CSV based on column value patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional


class ExtractorError(Exception):
    def __str__(self) -> str:
        return f"ExtractorError: {self.args[0]}"


@dataclass
class ExtractResult:
    headers: List[str]
    rows: List[Dict[str, str]]
    original_count: int
    column: str
    pattern: str
    _matched: List[Dict[str, str]] = field(default_factory=list, repr=False)

    @property
    def matched_count(self) -> int:
        return len(self._matched)

    @property
    def unmatched_count(self) -> int:
        return self.original_count - self.matched_count

    @property
    def match_rate(self) -> float:
        if self.original_count == 0:
            return 0.0
        return round(self.matched_count / self.original_count, 4)


def _validate(
    headers: List[str],
    column: str,
    pattern: str,
) -> None:
    if column not in headers:
        raise ExtractorError(f"column '{column}' not found in headers")
    if not pattern:
        raise ExtractorError("pattern must not be empty")
    try:
        re.compile(pattern)
    except re.error as exc:
        raise ExtractorError(f"invalid regex pattern: {exc}") from exc


def extract(
    headers: List[str],
    rows: List[Dict[str, str]],
    column: str,
    pattern: str,
    invert: bool = False,
) -> ExtractResult:
    """Return rows where *column* matches *pattern* (regex).

    If *invert* is True, return rows that do NOT match.
    """
    _validate(headers, column, pattern)
    regex = re.compile(pattern)
    matched = [
        row for row in rows
        if bool(regex.search(row.get(column, ""))) ^ invert
    ]
    result = ExtractResult(
        headers=list(headers),
        rows=matched,
        original_count=len(rows),
        column=column,
        pattern=pattern,
    )
    result._matched = matched
    return result
