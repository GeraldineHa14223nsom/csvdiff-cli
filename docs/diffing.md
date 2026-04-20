# Cell-Level Diffing

`csvdiff differ` provides character-level diffing for modified rows, letting you
see exactly which cells changed and how similar the old and new values are.

## Python API

```python
from csvdiff.differ import diff_modified

modified = [
    {
        "old": {"id": "1", "name": "Alice", "score": "80"},
        "new": {"id": "1", "name": "Alicia", "score": "95"},
    }
]

result = diff_modified(modified, key_columns=["id"])

for row in result.rows:
    print(f"Row key: {row.key}  changed columns: {row.changed_columns}")
    for cell in row.cells:
        if cell.is_changed:
            print(f"  {cell.column}: {cell.old_value!r} → {cell.new_value!r}  (similarity {cell.ratio:.0%})")
```

### Output

```
Row key: 1  changed columns: ['name', 'score']
  name: 'Alice' → 'Alicia'  (similarity 91%)
  score: '80' → '95'  (similarity 0%)
```

## Data model

| Class | Key attributes |
|---|---|
| `DifferResult` | `rows`, `total_changed_cells` |
| `RowDiff` | `key`, `cells`, `changed_columns`, `change_count` |
| `CellDiff` | `column`, `old_value`, `new_value`, `ratio`, `is_changed`, `opcodes` |

### `CellDiff.ratio`

A float in `[0.0, 1.0]` computed via `difflib.SequenceMatcher`.  
`1.0` means the values are identical; `0.0` means they share no characters.

### `CellDiff.opcodes`

The raw `SequenceMatcher.get_opcodes()` output — useful for rendering
colour-coded inline diffs in a terminal or HTML report.

## Integration with `core.diff`

Pass the `modified` list from a `DiffResult` directly:

```python
from csvdiff.core import diff
from csvdiff.differ import diff_modified

diff_result = diff("old.csv", "new.csv", key_columns=["id"])
cell_result = diff_modified(diff_result.modified, key_columns=["id"])
print(f"{cell_result.total_changed_cells} cells changed")
```

## Errors

`DifferError` is raised when:

- The `modified` argument is not a list.
- Any entry is missing an `"old"` or `"new"` key.
