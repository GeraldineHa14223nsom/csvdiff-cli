"""Generate and apply patch objects from DiffResult instances."""

from __future__ import annotations

import json
from typing import IO, Any

from csvdiff.core import DiffResult


def to_patch(result: DiffResult, keys: list[str]) -> dict[str, Any]:
    """Serialize a DiffResult into a structured patch dictionary."""
    return {
        "keys": keys,
        "added": result.added,
        "removed": result.removed,
        "modified": [
            {
                "key": entry["key"],
                "before": entry["before"],
                "after": entry["after"],
            }
            for entry in result.modified
        ],
    }


def write_patch(result: DiffResult, keys: list[str], fp: IO[str]) -> None:
    """Write a JSON patch derived from *result* to the file-like object *fp*."""
    patch = to_patch(result, keys)
    json.dump(patch, fp, indent=2)
    fp.write("\n")


def load_patch(fp: IO[str]) -> dict[str, Any]:
    """Load a patch dictionary from a JSON file-like object."""
    return json.load(fp)


def apply_patch(rows: list[dict], patch: dict[str, Any]) -> list[dict]:
    """Apply *patch* to *rows*, returning the patched list of rows.

    Rows are matched by the key columns recorded in the patch.
    """
    keys: list[str] = patch["keys"]

    def _key(row: dict) -> tuple:
        return tuple(row.get(k, "") for k in keys)

    index: dict[tuple, dict] = {_key(r): r for r in rows}

    # Apply removals
    for row in patch.get("removed", []):
        index.pop(_key(row), None)

    # Apply modifications
    for entry in patch.get("modified", []):
        k = tuple(entry["key"][col] for col in keys)
        if k in index:
            index[k] = entry["after"]

    # Apply additions
    for row in patch.get("added", []):
        index[_key(row)] = row

    return list(index.values())
