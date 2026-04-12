"""Output formatters for DiffResult — supports text, JSON, and CSV."""

import csv
import io
import json
from typing import Dict, List, Tuple

from csvdiff.core import DiffResult


def _row_to_str(row: Dict) -> str:
    return ", ".join(f"{k}={v}" for k, v in row.items())


def format_text(result: DiffResult) -> str:
    """Human-readable text diff output."""
    lines: List[str] = []
    summary = result.summary()
    lines.append(
        f"Summary: {summary['added']} added, {summary['removed']} removed, "
        f"{summary['modified']} modified, {summary['unchanged']} unchanged"
    )
    if result.added:
        lines.append("\n--- ADDED ---")
        for row in result.added:
            lines.append(f"  + {_row_to_str(row)}")
    if result.removed:
        lines.append("\n--- REMOVED ---")
        for row in result.removed:
            lines.append(f"  - {_row_to_str(row)}")
    if result.modified:
        lines.append("\n--- MODIFIED ---")
        for old, new in result.modified:
            lines.append(f"  < {_row_to_str(old)}")
            lines.append(f"  > {_row_to_str(new)}")
    return "\n".join(lines)


def format_json(result: DiffResult) -> str:
    """JSON diff output."""
    payload = {
        "summary": result.summary(),
        "added": result.added,
        "removed": result.removed,
        "modified": [
            {"before": old, "after": new} for old, new in result.modified
        ],
    }
    return json.dumps(payload, indent=2)


def format_csv(result: DiffResult) -> str:
    """CSV diff output with a leading '_diff' status column."""
    buf = io.StringIO()
    all_rows: List[Tuple[str, Dict]] = (
        [("added", r) for r in result.added]
        + [("removed", r) for r in result.removed]
        + [("modified_before", old) for old, _ in result.modified]
        + [("modified_after", _, ) for _, new in result.modified]
    )
    # rebuild properly
    flat_rows: List[Dict] = []
    for status, row in [("added", r) for r in result.added]:
        flat_rows.append({"_diff": status, **row})
    for status, row in [("removed", r) for r in result.removed]:
        flat_rows.append({"_diff": status, **row})
    for old, new in result.modified:
        flat_rows.append({"_diff": "modified_before", **old})
        flat_rows.append({"_diff": "modified_after", **new})

    if not flat_rows:
        return "_diff\n(no differences)"

    fieldnames = list(flat_rows[0].keys())
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(flat_rows)
    return buf.getvalue()


FORMAT_MAP = {
    "text": format_text,
    "json": format_json,
    "csv": format_csv,
}


def render(result: DiffResult, fmt: str = "text") -> str:
    """Render a DiffResult using the named formatter."""
    formatter = FORMAT_MAP.get(fmt)
    if formatter is None:
        raise ValueError(f"Unknown format '{fmt}'. Choose from: {list(FORMAT_MAP)}.")
    return formatter(result)
