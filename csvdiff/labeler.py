"""Assign sequential or custom labels to groups of rows based on a column value."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class LabelerError(Exception):
    def __str__(self) -> str:
        return f"LabelerError: {self.args[0]}"


@dataclass
class LabelResult:
    rows: List[Dict[str, str]]
    label_column: str
    group_column: str
    label_map: Dict[str, str]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def group_count(self) -> int:
        return len(self.label_map)


def _validate(rows: List[Dict[str, str]], group_column: str) -> None:
    if not rows:
        return
    headers = list(rows[0].keys())
    if group_column not in headers:
        raise LabelerError(
            f"group column '{group_column}' not found in headers: {headers}"
        )


def label_rows(
    rows: List[Dict[str, str]],
    group_column: str,
    label_column: str = "label",
    mapping: Optional[Dict[str, str]] = None,
    default: str = "",
) -> LabelResult:
    """Attach a label to every row based on the value of *group_column*.

    If *mapping* is provided it is used as-is; otherwise groups are assigned
    auto-incrementing numeric labels ("1", "2", …) in order of first
    appearance.
    """
    _validate(rows, group_column)

    if mapping is None:
        mapping = {}
        counter = 1
        for row in rows:
            val = row[group_column]
            if val not in mapping:
                mapping[val] = str(counter)
                counter += 1

    labeled: List[Dict[str, str]] = []
    for row in rows:
        new_row = dict(row)
        new_row[label_column] = mapping.get(row[group_column], default)
        labeled.append(new_row)

    return LabelResult(
        rows=labeled,
        label_column=label_column,
        group_column=group_column,
        label_map=dict(mapping),
    )
