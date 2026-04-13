"""Schema validation for CSV files before diffing."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SchemaError(Exception):
    message: str
    missing_columns: List[str] = field(default_factory=list)
    extra_columns: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        parts = [self.message]
        if self.missing_columns:
            parts.append(f"  Missing columns: {', '.join(self.missing_columns)}")
        if self.extra_columns:
            parts.append(f"  Extra columns:   {', '.join(self.extra_columns)}")
        return "\n".join(parts)


@dataclass
class SchemaResult:
    valid: bool
    errors: List[SchemaError] = field(default_factory=list)

    def raise_if_invalid(self) -> None:
        if not self.valid:
            raise SchemaError(
                "Schema validation failed",
                missing_columns=[c for e in self.errors for c in e.missing_columns],
                extra_columns=[c for e in self.errors for c in e.extra_columns],
            )


def validate_columns(
    left_headers: List[str],
    right_headers: List[str],
    key_columns: List[str],
    strict: bool = False,
) -> SchemaResult:
    """Validate that both CSVs share the required columns for diffing.

    Args:
        left_headers: Column names from the left (base) CSV.
        right_headers: Column names from the right (compare) CSV.
        key_columns: Columns that must be present in both files.
        strict: When True, both files must have identical column sets.

    Returns:
        A SchemaResult indicating validity and any errors found.
    """
    errors: List[SchemaError] = []

    left_set = set(left_headers)
    right_set = set(right_headers)

    # Key columns must exist in both files
    missing_in_left = [k for k in key_columns if k not in left_set]
    missing_in_right = [k for k in key_columns if k not in right_set]

    if missing_in_left:
        errors.append(
            SchemaError(
                "Key columns missing from left file",
                missing_columns=missing_in_left,
            )
        )
    if missing_in_right:
        errors.append(
            SchemaError(
                "Key columns missing from right file",
                missing_columns=missing_in_right,
            )
        )

    if strict:
        only_in_left = sorted(left_set - right_set)
        only_in_right = sorted(right_set - left_set)
        if only_in_left or only_in_right:
            errors.append(
                SchemaError(
                    "Column sets differ between files (strict mode)",
                    missing_columns=only_in_right,  # present in right but not left
                    extra_columns=only_in_left,      # present in left but not right
                )
            )

    return SchemaResult(valid=len(errors) == 0, errors=errors)
