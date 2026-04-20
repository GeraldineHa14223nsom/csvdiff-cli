"""Column-level value differ: computes character-level diffs for modified cells."""
from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class DifferError(Exception):
    def __str__(self) -> str:
        return f"DifferError: {self.args[0]}"


@dataclass
class CellDiff:
    column: str
    old_value: str
    new_value: str
    opcodes: List[tuple] = field(default_factory=list)

    @property
    def ratio(self) -> float:
        """Similarity ratio between old and new value (0.0 – 1.0)."""
        return difflib.SequenceMatcher(None, self.old_value, self.new_value).ratio()

    @property
    def is_changed(self) -> bool:
        return self.old_value != self.new_value


@dataclass
class RowDiff:
    key: str
    cells: List[CellDiff] = field(default_factory=list)

    @property
    def changed_columns(self) -> List[str]:
        return [c.column for c in self.cells if c.is_changed]

    @property
    def change_count(self) -> int:
        return len(self.changed_columns)


@dataclass
class DifferResult:
    rows: List[RowDiff] = field(default_factory=list)

    @property
    def total_changed_cells(self) -> int:
        return sum(r.change_count for r in self.rows)


def _diff_cells(old_row: Dict[str, str], new_row: Dict[str, str]) -> List[CellDiff]:
    columns = set(old_row) | set(new_row)
    cells = []
    for col in sorted(columns):
        old_val = old_row.get(col, "")
        new_val = new_row.get(col, "")
        sm = difflib.SequenceMatcher(None, old_val, new_val)
        cells.append(CellDiff(
            column=col,
            old_value=old_val,
            new_value=new_val,
            opcodes=sm.get_opcodes(),
        ))
    return cells


def diff_modified(
    modified: List[Dict],
    key_columns: Optional[List[str]] = None,
) -> DifferResult:
    """Compute cell-level diffs for a list of modified-row records.

    Each record in *modified* must have ``"old"`` and ``"new"`` sub-dicts
    (the format produced by ``csvdiff.core.diff``).
    """
    if not isinstance(modified, list):
        raise DifferError("modified must be a list of dicts with 'old' and 'new' keys")

    rows: List[RowDiff] = []
    for entry in modified:
        if "old" not in entry or "new" not in entry:
            raise DifferError("each modified entry must contain 'old' and 'new' keys")
        old_row: Dict[str, str] = entry["old"]
        new_row: Dict[str, str] = entry["new"]
        if key_columns:
            key = "|".join(str(old_row.get(k, "")) for k in key_columns)
        else:
            key = str(next(iter(old_row.values()), ""))
        cells = _diff_cells(old_row, new_row)
        rows.append(RowDiff(key=key, cells=cells))

    return DifferResult(rows=rows)
