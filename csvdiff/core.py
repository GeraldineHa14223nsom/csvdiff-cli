"""Core diffing logic for csvdiff-cli."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

Row = Dict[str, str]


@dataclass
class DiffResult:
    added: List[Row] = field(default_factory=list)
    removed: List[Row] = field(default_factory=list)
    modified: List[Tuple[Row, Row]] = field(default_factory=list)
    unchanged: List[Row] = field(default_factory=list)


def has_differences(result: DiffResult) -> bool:
    return bool(result.added or result.removed or result.modified)


def summary(result: DiffResult) -> str:
    return (
        f"added={len(result.added)} removed={len(result.removed)} "
        f"modified={len(result.modified)} unchanged={len(result.unchanged)}"
    )


def _read_csv(path: Path) -> List[Row]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _make_key(row: Row, keys: Sequence[str]) -> Tuple[str, ...]:
    try:
        return tuple(row[k] for k in keys)
    except KeyError as exc:
        raise KeyError(f"Key column {exc} not found in row: {list(row.keys())}") from exc


def diff_files(
    old_path: Path,
    new_path: Path,
    keys: Sequence[str],
    ignore_columns: Sequence[str] = (),
) -> DiffResult:
    old_rows = _read_csv(old_path)
    new_rows = _read_csv(new_path)

    def _strip(row: Row) -> Row:
        return {k: v for k, v in row.items() if k not in ignore_columns}

    old_index: Dict[Tuple[str, ...], Row] = {_make_key(r, keys): _strip(r) for r in old_rows}
    new_index: Dict[Tuple[str, ...], Row] = {_make_key(r, keys): _strip(r) for r in new_rows}

    result = DiffResult()

    for key, old_row in old_index.items():
        if key not in new_index:
            result.removed.append(old_row)
        else:
            new_row = new_index[key]
            if old_row != new_row:
                result.modified.append((old_row, new_row))
            else:
                result.unchanged.append(old_row)

    for key, new_row in new_index.items():
        if key not in old_index:
            result.added.append(new_row)

    return result
