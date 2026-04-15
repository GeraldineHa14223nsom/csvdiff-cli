"""Type-casting module: convert CSV column values to int, float, bool, or str."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

_SUPPORTED = ("int", "float", "bool", "str")


class CasterError(Exception):
    def __str__(self) -> str:  # pragma: no cover
        return self.args[0]


@dataclass
class CastResult:
    headers: List[str]
    rows: List[Dict[str, str]]
    cast_count: int = 0
    error_count: int = 0
    errors: List[str] = field(default_factory=list)


def _validate_type(type_name: str) -> None:
    if type_name not in _SUPPORTED:
        raise CasterError(
            f"Unsupported type '{type_name}'. Choose from: {', '.join(_SUPPORTED)}"
        )


def _cast_value(value: str, type_name: str) -> str:
    """Return the value coerced to *type_name* and back to str."""
    if type_name == "int":
        return str(int(value))
    if type_name == "float":
        return str(float(value))
    if type_name == "bool":
        if value.strip().lower() in ("1", "true", "yes"):
            return "True"
        if value.strip().lower() in ("0", "false", "no", ""):
            return "False"
        raise ValueError(f"Cannot cast '{value}' to bool")
    return str(value)  # str is a no-op


def cast_columns(
    headers: List[str],
    rows: Iterable[Dict[str, str]],
    mapping: Dict[str, str],
    *,
    strict: bool = False,
) -> CastResult:
    """Cast columns according to *mapping* ({column: type_name}).

    Parameters
    ----------
    strict:
        When True, raise CasterError on the first conversion failure instead
        of recording the error and keeping the original value.
    """
    for col, type_name in mapping.items():
        _validate_type(type_name)
        if col not in headers:
            raise CasterError(f"Column '{col}' not found in headers")

    cast_count = 0
    error_count = 0
    errors: List[str] = []
    out_rows: List[Dict[str, str]] = []

    for row in rows:
        new_row = dict(row)
        for col, type_name in mapping.items():
            original = row.get(col, "")
            try:
                new_row[col] = _cast_value(original, type_name)
                cast_count += 1
            except (ValueError, TypeError) as exc:
                msg = f"Row {len(out_rows) + 1}, column '{col}': {exc}"
                if strict:
                    raise CasterError(msg) from exc
                errors.append(msg)
                error_count += 1
        out_rows.append(new_row)

    return CastResult(
        headers=headers,
        rows=out_rows,
        cast_count=cast_count,
        error_count=error_count,
        errors=errors,
    )
