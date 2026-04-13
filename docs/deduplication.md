# Deduplication

`csvdiff` can detect and remove duplicate rows from a CSV file based on one or
more **key columns** before performing a diff or reconciliation.

## Why deduplication matters

Duplicate rows with the same key can cause false positives in diff output.  
Stripping them first produces a cleaner, more meaningful comparison.

## Python API

```python
from csvdiff.deduplicator import deduplicate, find_duplicate_keys

rows = [
    {"id": "1", "name": "Alice", "score": "90"},
    {"id": "2", "name": "Bob",   "score": "85"},
    {"id": "1", "name": "Alice", "score": "95"},  # duplicate
]

# Keep the first occurrence of each key (default)
result = deduplicate(rows, keys=["id"])
print(result.unique_count)     # 2
print(result.duplicate_count)  # 1

# Keep the last occurrence instead
result_last = deduplicate(rows, keys=["id"], keep="last")

# Inspect which keys have duplicates
groups = find_duplicate_keys(rows, keys=["id"])
# {('1',): [ {id:1, score:90}, {id:1, score:95} ]}
```

## `DedupeResult` fields

| Field | Type | Description |
|-------|------|-------------|
| `unique` | `list[dict]` | Rows after deduplication |
| `duplicates` | `list[tuple[dict, int]]` | Removed rows paired with the index of the surviving row |
| `unique_count` | `int` | Number of unique rows |
| `duplicate_count` | `int` | Number of removed rows |

## `keep` strategies

| Value | Behaviour |
|-------|-----------|
| `"first"` *(default)* | Retain the earliest row for each key |
| `"last"` | Retain the latest row for each key |

## Composite keys

Pass multiple column names to `keys` to form a composite key:

```python
result = deduplicate(rows, keys=["country", "city"])
```

## Errors

`DeduplicatorError` is raised when:

- A key column is missing from a row.
- An unsupported `keep` strategy is supplied.
