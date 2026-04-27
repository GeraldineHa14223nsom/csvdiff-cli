# Row Extraction

The `extractor` module filters rows from a CSV file where a specified column
matches a regular-expression pattern.

## API

```python
from csvdiff.extractor import extract

result = extract(
    headers=["id", "name", "city"],
    rows=rows,
    column="city",
    pattern=r"New York",
)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `headers` | `list[str]` | Column names |
| `rows` | `list[dict]` | Input rows |
| `column` | `str` | Column to match against |
| `pattern` | `str` | Regular-expression pattern |
| `invert` | `bool` | If `True`, return non-matching rows (default `False`) |

### ExtractResult

| Attribute | Description |
|-----------|-------------|
| `rows` | Filtered rows |
| `original_count` | Total rows before filtering |
| `matched_count` | Number of rows that matched |
| `unmatched_count` | Rows that did not match |
| `match_rate` | Fraction of rows matched (0–1) |
| `column` | Column used for matching |
| `pattern` | Pattern used for matching |

## Errors

`ExtractorError` is raised when:

- The specified column does not exist in `headers`.
- The pattern string is empty.
- The pattern is not a valid regular expression.

## Examples

### Keep only rows from New York

```python
result = extract(headers, rows, column="city", pattern="New York")
print(result.matched_count)   # 2
print(result.match_rate)      # 0.4
```

### Exclude rows matching a pattern (invert)

```python
result = extract(headers, rows, column="status", pattern="inactive", invert=True)
# Returns all rows where status != 'inactive'
```

### Use a full regex

```python
result = extract(headers, rows, column="email", pattern=r".+@example\.com$")
```
