"""Tag rows with a label based on column value membership in a set."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Set


class TaggerError(Exception):
    def __str__(self) -> str:
        return f"TaggerError: {self.args[0]}"


@dataclass
class TagResult:
    headers: List[str]
    rows: List[Dict[str, str]]
    tag_column: str
    tagged_count: int
    untagged_count: int


def _validate(rows: List[Dict[str, str]], column: str, tag_column: str) -> None:
    if not rows:
        return
    if column not in rows[0]:
        raise TaggerError(f"Column '{column}' not found in headers")
    if tag_column in rows[0]:
        raise TaggerError(f"Tag column '{tag_column}' already exists in headers")


def tag_rows(
    rows: List[Dict[str, str]],
    column: str,
    values: Set[str],
    tag_column: str = "tag",
    match_label: str = "match",
    no_match_label: str = "",
) -> TagResult:
    """Add a tag column based on whether a column value is in *values*."""
    _validate(rows, column, tag_column)

    original_headers = list(rows[0].keys()) if rows else []
    new_headers = original_headers + [tag_column]

    tagged_count = 0
    untagged_count = 0
    out: List[Dict[str, str]] = []

    for row in rows:
        label = match_label if row[column] in values else no_match_label
        if label == match_label:
            tagged_count += 1
        else:
            untagged_count += 1
        out.append({**row, tag_column: label})

    return TagResult(
        headers=new_headers,
        rows=out,
        tag_column=tag_column,
        tagged_count=tagged_count,
        untagged_count=untagged_count,
    )
