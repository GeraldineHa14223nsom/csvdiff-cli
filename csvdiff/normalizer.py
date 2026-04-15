"""Normalize CSV rows by stripping whitespace, fixing case, and standardizing empty values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class NormalizerError(Exception):
    def __str__(self) -> str:
        return f"NormalizerError: {self.args[0]}"


@dataclass
class NormalizeResult:
    rows: List[Dict[str, str]]
    original_count: int
    modified_count: int

    def unchanged_count(self) -> int:
        return self.original_count - self.modified_count


_VALID_CASE_MODES = ("lower", "upper", "title", None)


def _normalize_row(
    row: Dict[str, str],
    *,
    strip: bool,
    case: Optional[str],
    empty_value: Optional[str],
    columns: Optional[List[str]],
) -> tuple[Dict[str, str], bool]:
    """Return (normalized_row, was_changed)."""
    changed = False
    result: Dict[str, str] = {}
    for key, value in row.items():
        if columns is not None and key not in columns:
            result[key] = value
            continue
        new_value = value
        if strip:
            new_value = new_value.strip()
        if case == "lower":
            new_value = new_value.lower()
        elif case == "upper":
            new_value = new_value.upper()
        elif case == "title":
            new_value = new_value.title()
        if empty_value is not None and new_value == "":
            new_value = empty_value
        if new_value != value:
            changed = True
        result[key] = new_value
    return result, changed


def normalize_rows(
    rows: List[Dict[str, str]],
    *,
    strip: bool = True,
    case: Optional[str] = None,
    empty_value: Optional[str] = None,
    columns: Optional[List[str]] = None,
) -> NormalizeResult:
    """Normalize a list of CSV row dicts.

    Args:
        rows: Input rows.
        strip: Strip leading/trailing whitespace from values.
        case: Optional case transformation: 'lower', 'upper', or 'title'.
        empty_value: Replace empty strings with this value (e.g. 'N/A').
        columns: Restrict normalization to these columns; None means all.

    Returns:
        NormalizeResult with normalized rows and change counts.
    """
    if case not in _VALID_CASE_MODES:
        raise NormalizerError(
            f"Invalid case mode {case!r}. Choose from: lower, upper, title."
        )
    if columns is not None:
        all_keys = {k for row in rows for k in row}
        unknown = set(columns) - all_keys
        if unknown:
            raise NormalizerError(
                f"Unknown columns for normalization: {sorted(unknown)}"
            )

    normalized: List[Dict[str, str]] = []
    modified_count = 0
    for row in rows:
        new_row, changed = _normalize_row(
            row, strip=strip, case=case, empty_value=empty_value, columns=columns
        )
        normalized.append(new_row)
        if changed:
            modified_count += 1

    return NormalizeResult(
        rows=normalized,
        original_count=len(rows),
        modified_count=modified_count,
    )
