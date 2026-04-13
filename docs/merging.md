# Merging CSV Files

`csvdiff` includes a merge module that lets you apply a computed diff back onto
a base CSV file to produce a reconciled output.

## Overview

The `merge()` function in `csvdiff.merger` accepts:

| Parameter  | Type          | Description                                      |
|------------|---------------|--------------------------------------------------|
| `diff`     | `DiffResult`  | The diff produced by `csvdiff.core.diff()`       |
| `keys`     | `list[str]`   | Column names used as the composite row key       |
| `strategy` | `str`         | Conflict resolution strategy (see below)         |
| `base`     | `list[dict]`  | Optional base rows to merge into                 |

## Conflict Resolution Strategies

### `ours` (default)
When a row was modified in the diff, keep the **old** (left) value.
The conflict is recorded in `MergeResult.conflicts` but does not raise.

### `theirs`
When a row was modified in the diff, keep the **new** (right) value.
Conflicts are still recorded for inspection.

### `raise`
Raise a `MergeError` immediately upon encountering any modified row.
Useful when you require a clean, conflict-free merge.

## Example

```python
from csvdiff.core import diff
from csvdiff.merger import merge

result = diff(left_rows, right_rows, keys=["id"])
merged = merge(result, keys=["id"], strategy="theirs", base=left_rows)

if merged.has_conflicts:
    print(f"{len(merged.conflicts)} conflict(s) resolved with 'theirs' strategy")

for row in merged.rows:
    print(row)
```

## MergeResult

```python
@dataclass
class MergeResult:
    rows: list[dict]                              # final merged rows
    conflicts: list[tuple[dict, dict]]            # (old, new) pairs that conflicted

    @property
    def has_conflicts(self) -> bool: ...
```

## Error Handling

`MergeError` is raised when:
- An unknown `strategy` string is provided.
- `strategy="raise"` and at least one modified row is present in the diff.
