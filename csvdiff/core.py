"""Core CSV diffing logic for csvdiff-cli."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import csv
import io


@dataclass
class DiffResult:
    """Holds the result of diffing two CSV files."""
    added: List[Dict] = field(default_factory=list)
    removed: List[Dict] = field(default_factory=list)
    modified: List[Tuple[Dict, Dict]] = field(default_factory=list)
    unchanged: List[Dict] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    def summary(self) -> Dict[str, int]:
        return {
            "added": len(self.added),
            "removed": len(self.removed),
            "modified": len(self.modified),
            "unchanged": len(self.unchanged),
        }


def _read_csv(source: str) -> Tuple[List[str], List[Dict]]:
    """Read CSV from a file path or string, returning headers and rows."""
    try:
        with open(source, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            rows = [dict(row) for row in reader]
    except (FileNotFoundError, OSError):
        reader = csv.DictReader(io.StringIO(source))
        headers = reader.fieldnames or []
        rows = [dict(row) for row in reader]
    return list(headers), rows


def _make_key(row: Dict, key_columns: List[str]) -> Tuple:
    """Build a hashable key from specified columns."""
    return tuple(row.get(col, "") for col in key_columns)


def diff_csv(
    source_a: str,
    source_b: str,
    key_columns: List[str],
    ignore_columns: Optional[List[str]] = None,
) -> DiffResult:
    """Diff two CSV sources by key columns.

    Args:
        source_a: File path or CSV string for the base dataset.
        source_b: File path or CSV string for the target dataset.
        key_columns: Columns that uniquely identify each row.
        ignore_columns: Columns to exclude from comparison.

    Returns:
        A DiffResult containing added, removed, modified, and unchanged rows.
    """
    ignore: Set[str] = set(ignore_columns or [])
    _, rows_a = _read_csv(source_a)
    _, rows_b = _read_csv(source_b)

    index_a: Dict[Tuple, Dict] = {_make_key(r, key_columns): r for r in rows_a}
    index_b: Dict[Tuple, Dict] = {_make_key(r, key_columns): r for r in rows_b}

    result = DiffResult()

    for key, row_b in index_b.items():
        if key not in index_a:
            result.added.append(row_b)
        else:
            row_a = index_a[key]
            a_cmp = {k: v for k, v in row_a.items() if k not in ignore}
            b_cmp = {k: v for k, v in row_b.items() if k not in ignore}
            if a_cmp != b_cmp:
                result.modified.append((row_a, row_b))
            else:
                result.unchanged.append(row_b)

    for key, row_a in index_a.items():
        if key not in index_b:
            result.removed.append(row_a)

    return result
