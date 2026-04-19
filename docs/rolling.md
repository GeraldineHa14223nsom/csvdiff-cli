# Rolling Window Calculations

The `roll` command computes rolling (sliding window) statistics over a numeric column in a CSV file.

## Usage

```
csvdiff roll <file> --column <col> --window <n> [--func mean|sum|min|max] [--new-column <name>] [--output <file>]
```

## Arguments

| Argument | Description |
|---|---|
| `file` | Input CSV file |
| `--column` | Numeric column to compute over |
| `--window` | Number of rows in the sliding window |
| `--func` | Aggregation function: `mean` (default), `sum`, `min`, `max` |
| `--new-column` | Name of the output column (auto-generated if omitted) |
| `--output` | Write result to file instead of stdout |

## Examples

### 3-row rolling mean

```
csvdiff roll prices.csv --column close --window 3
```

Adds a column `close_rolling_mean_3` to each row. The first `window - 1` rows will have an empty value.

### Rolling sum with custom output column

```
csvdiff roll sales.csv --column revenue --window 7 --func sum --new-column weekly_revenue
```

## Python API

```python
from csvdiff.roller import rolling

result = rolling(rows, column="price", window=5, func="mean")
for row in result.rows:
    print(row)
```

### RollResult fields

- `rows` — list of dicts with the new column appended
- `column` — source column name
- `window` — window size used
- `new_column` — name of the generated column
- `computed` — number of rows where the statistic was computed

## Notes

- Rows with fewer than `window` preceding rows (including themselves) receive an empty string value.
- Non-numeric values in the target column raise a `RollerError`.
