# Imputation

The `imputer` module fills empty (blank) cells in CSV data with configurable replacement values.

## Usage

```python
from csvdiff.imputer import impute

result = impute(
    headers=["id", "name", "score"],
    rows=rows,
    fill_value="N/A",
)
print(result.filled_count)  # total cells filled
print(result.column_counts)  # per-column breakdown
```

## Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `fill_value` | `str` | Default value used for all empty cells (default `""`) |
| `fill_map` | `dict` | Per-column fill values; overrides `fill_value` for named columns |
| `columns` | `list` | Restrict filling to these columns when using `fill_value` |

## Per-column values

```python
result = impute(
    headers=headers,
    rows=rows,
    fill_map={"score": "0", "category": "unknown"},
)
```

## Result

`ImputeResult` exposes:

- `headers` — original header list
- `rows` — transformed rows
- `filled_count` — total number of cells that were filled
- `column_counts` — mapping of column name → number of cells filled

## Errors

`ImputerError` is raised when `fill_map` references a column not present in `headers`.
