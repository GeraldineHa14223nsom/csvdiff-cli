# CSV Join

The `join` sub-command merges two CSV files on a shared key column, similar to a SQL JOIN.

## Usage

```
csvdiff join LEFT RIGHT --key COLUMN [--how TYPE] [--output FILE]
             [--include-left-only] [--include-right-only]
```

### Arguments

| Argument | Description |
|---|---|
| `LEFT` | Path to the left CSV file |
| `RIGHT` | Path to the right CSV file |
| `--key` | Column name to join on (required) |
| `--how` | Join type: `inner`, `left`, `right`, `outer` (default: `inner`) |
| `--output` / `-o` | Write result to file instead of stdout |
| `--include-left-only` | Append rows present only in the left file |
| `--include-right-only` | Append rows present only in the right file |

## Join Types

- **inner** – only rows whose key appears in *both* files.
- **left** – all rows from the left file; unmatched left rows collected separately.
- **right** – all rows from the right file; unmatched right rows collected separately.
- **outer** – all rows from both files.

## Conflicting Column Names

When both files share a non-key column name the suffixes `_left` and `_right`
are appended automatically:

```
id,value_left,value_right
1,a,b
```

## Programmatic API

```python
from csvdiff.joiner import join

result = join(left_rows, right_rows, key="id", how="outer")
print(result.rows)       # matched rows
print(result.left_only)  # unmatched left rows
print(result.right_only) # unmatched right rows
```

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Join error (bad key, unknown join type) |
| 2 | Input file not found |
