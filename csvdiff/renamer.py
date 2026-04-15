"""Column renaming utilities for CSV rows."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List


class RenamerError(Exception):
    def __str__(self) -> str:
        return f"RenamerError: {self.args[0]}"


@dataclass(frozen=True)
class RenameResult:
    rows: List[Dict[str, str]]
    mapping: Dict[str, str]  # old_name -> new_name


def _validate_mapping(
    mapping: Dict[str, str],
    headers: Iterable[str],
) -> None:
    """Raise RenamerError if any source column is absent from headers."""
    header_set = set(headers)
    missing = [col for col in mapping if col not in header_set]
    if missing:
        raise RenamerError(
            f"Column(s) not found in source: {', '.join(sorted(missing))}"
        )


def rename_columns(
    rows: List[Dict[str, str]],
    mapping: Dict[str, str],
) -> RenameResult:
    """Return a new list of rows with columns renamed according to *mapping*.

    Parameters
    ----------
    rows:
        Input rows as list-of-dicts.
    mapping:
        Dict mapping old column names to new column names.
        Columns absent from the mapping are passed through unchanged.
    """
    if not rows:
        return RenameResult(rows=[], mapping=mapping)

    _validate_mapping(mapping, rows[0].keys())

    renamed: List[Dict[str, str]] = [
        {mapping.get(k, k): v for k, v in row.items()}
        for row in rows
    ]
    return RenameResult(rows=renamed, mapping=mapping)


def iter_renamed(
    rows: Iterable[Dict[str, str]],
    mapping: Dict[str, str],
) -> Iterator[Dict[str, str]]:
    """Streaming variant – yields renamed rows one at a time."""
    for row in rows:
        yield {mapping.get(k, k): v for k, v in row.items()}
