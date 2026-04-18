"""Bin numeric column values into labelled buckets."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional


class BinnerError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class BinResult:
    rows: List[Dict[str, str]]
    headers: List[str]
    column: str
    bin_column: str
    boundaries: List[float]
    labels: List[str]
    bin_counts: Dict[str, int] = field(default_factory=dict)


def _validate(rows: list, column: str, boundaries: list, labels: list) -> None:
    if not rows:
        return
    if column not in rows[0]:
        raise BinnerError(f"Column '{column}' not found in headers.")
    if len(boundaries) < 2:
        raise BinnerError("At least two boundary values are required.")
    expected = len(boundaries) - 1
    if labels and len(labels) != expected:
        raise BinnerError(
            f"Expected {expected} labels for {expected} bins, got {len(labels)}."
        )


def _make_labels(boundaries: List[float], labels: Optional[List[str]]) -> List[str]:
    if labels:
        return labels
    result = []
    for i in range(len(boundaries) - 1):
        result.append(f"{boundaries[i]}-{boundaries[i+1]}")
    return result


def bin_column(
    rows: List[Dict[str, str]],
    column: str,
    boundaries: List[float],
    labels: Optional[List[str]] = None,
    bin_column: str = "",
    out_of_range: str = "other",
) -> BinResult:
    _validate(rows, column, boundaries, labels)
    resolved_labels = _make_labels(boundaries, labels)
    col_name = bin_column or f"{column}_bin"
    counts: Dict[str, int] = {lbl: 0 for lbl in resolved_labels}
    counts[out_of_range] = 0
    out_rows = []
    for row in rows:
        try:
            val = float(row[column])
        except (ValueError, KeyError):
            label = out_of_range
        else:
            label = out_of_range
            for i in range(len(boundaries) - 1):
                if boundaries[i] <= val < boundaries[i + 1]:
                    label = resolved_labels[i]
                    break
        counts[label] = counts.get(label, 0) + 1
        out_rows.append({**row, col_name: label})
    headers = list(rows[0].keys()) + [col_name] if rows else [col_name]
    return BinResult(
        rows=out_rows,
        headers=headers,
        column=column,
        bin_column=col_name,
        boundaries=boundaries,
        labels=resolved_labels,
        bin_counts=counts,
    )
