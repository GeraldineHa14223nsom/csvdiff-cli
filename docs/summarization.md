# CSV Summarization

The `summarizer` module provides a single-pass summary of every column in a CSV
dataset, giving you counts, fill rates, and basic numeric statistics without
loading the entire file into memory more than once.

## Quick start

```python
from csvdiff.summarizer import summarize

rows = [
    {"id": "1", "name": "Alice", "score": "90"},
    {"id": "2", "name": "Bob",   "score": "80"},
    {"id": "3", "name": "",      "score": "70"},
]

result = summarize(rows)
for col in result.columns:
    print(col.column, col.fill_rate, col.mean_value)
```

## API

### `summarize(rows, columns=None) -> SummaryResult`

Compute per-column statistics for *rows*.

| Parameter | Type | Description |
|-----------|------|-------------|
| `rows` | `list[dict]` | Rows as returned by `csv.DictReader` |
| `columns` | `list[str] \| None` | Subset of columns to analyse; `None` = all |

Raises `SummarizerError` if any name in `columns` is not present in the data.

### `SummaryResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `columns` | `list[ColumnSummary]` | One entry per analysed column |
| `row_count` | `int` | Total number of input rows |
| `get(column)` | `ColumnSummary \| None` | Look up a column by name |

### `ColumnSummary`

| Attribute | Type | Description |
|-----------|------|-------------|
| `column` | `str` | Column name |
| `count` | `int` | Total rows seen |
| `non_empty` | `int` | Rows with a non-blank value |
| `empty_count` | `int` | Rows with a blank value |
| `fill_rate` | `float` | `non_empty / count` |
| `numeric_count` | `int` | Rows whose value parses as a float |
| `min_value` | `float \| None` | Minimum numeric value, or `None` |
| `max_value` | `float \| None` | Maximum numeric value, or `None` |
| `mean_value` | `float \| None` | Arithmetic mean of numeric values |

## Error handling

```python
from csvdiff.summarizer import SummarizerError

try:
    result = summarize(rows, columns=["nonexistent"])
except SummarizerError as exc:
    print(exc)  # SummarizerError: Unknown columns: ['nonexistent']
```

## Notes

- Empty input (`rows=[]`) returns a `SummaryResult` with `row_count=0` and an
  empty `columns` list — no exception is raised.
- A value is considered *numeric* if `float(value)` succeeds; blank strings are
  treated as non-numeric.
- `min_value`, `max_value`, and `mean_value` are all `None` for columns that
  contain no parseable numbers.
