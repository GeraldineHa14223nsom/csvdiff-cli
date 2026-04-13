"""Column and value transformation utilities for CSV diff pipeline."""

from __future__ import annotations

from typing import Callable, Dict, Iterable, List

TransformFn = Callable[[str], str]


class TransformError(ValueError):
    """Raised when a transform cannot be applied."""


_BUILTIN: Dict[str, TransformFn] = {
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
    "int": lambda v: str(int(v)),
    "float": lambda v: str(float(v)),
}


def get_transform(name: str) -> TransformFn:
    """Return a built-in transform function by name."""
    try:
        return _BUILTIN[name]
    except KeyError:
        raise TransformError(
            f"Unknown transform {name!r}. Available: {sorted(_BUILTIN)}"
        )


def apply_transforms(
    rows: Iterable[Dict[str, str]],
    transforms: Dict[str, str],
) -> List[Dict[str, str]]:
    """Apply named transforms to specific columns in every row.

    Args:
        rows: Iterable of row dicts.
        transforms: Mapping of column name -> transform name.

    Returns:
        New list of row dicts with transformed values.

    Raises:
        TransformError: If a transform name is unknown or a value cannot be
            converted.
    """
    fns: Dict[str, TransformFn] = {
        col: get_transform(name) for col, name in transforms.items()
    }

    result: List[Dict[str, str]] = []
    for row in rows:
        new_row = dict(row)
        for col, fn in fns.items():
            if col in new_row:
                try:
                    new_row[col] = fn(new_row[col])
                except (ValueError, TypeError) as exc:
                    raise TransformError(
                        f"Transform failed for column {col!r}, "
                        f"value {new_row[col]!r}: {exc}"
                    ) from exc
        result.append(new_row)
    return result


def rename_columns(
    rows: Iterable[Dict[str, str]],
    renames: Dict[str, str],
) -> List[Dict[str, str]]:
    """Rename columns in every row.

    Args:
        rows: Iterable of row dicts.
        renames: Mapping of old column name -> new column name.

    Returns:
        New list of row dicts with renamed columns.
    """
    result: List[Dict[str, str]] = []
    for row in rows:
        new_row = {
            renames.get(k, k): v for k, v in row.items()
        }
        result.append(new_row)
    return result
