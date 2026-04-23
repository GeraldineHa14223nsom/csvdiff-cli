# Highlighting

The `highlighter` module scans a CSV column for rows whose values match a
regular-expression pattern and tags each row with a binary flag column.

## Basic usage

```python
from csvdiff.highlighter import highlight, match_rate

rows = [
    {"id": "1", "email": "alice@example.com"},
    {"id": "2", "email": "bob@corp.org"},
]

result = highlight(rows, column="email", pattern=r"example\.com")
print(result.match_count)   # 1
print(match_rate(result))   # 0.5
```

Each row in `result.rows` gains a new `_highlight` column set to `"1"` when
the cell matched or `"0"` otherwise.  The original list is **not** mutated.

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `rows` | `list[dict]` | — | Input rows |
| `column` | `str` | — | Column to search |
| `pattern` | `str` | — | Regular-expression pattern |
| `highlight_column` | `str` | `"_highlight"` | Name of the flag column added to each row |
| `case_sensitive` | `bool` | `False` | Whether the regex match is case-sensitive |

## Return value – `HighlightResult`

| Attribute | Description |
|---|---|
| `rows` | All rows with the flag column appended |
| `flagged` | Only the rows that matched |
| `column` | Column that was searched |
| `pattern` | Pattern that was used |
| `match_count` | Number of matching rows |

## Helper – `match_rate`

```python
rate = match_rate(result)  # float in [0, 1]
```

Returns the fraction of rows that matched.  Returns `0.0` for empty input.

## Errors

`HighlighterError` is raised when:

- The specified column does not exist in the row headers.
- The pattern is not a valid regular expression.
