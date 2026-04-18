# Binning

The `bin` command assigns numeric column values to discrete labelled buckets (bins).

## Usage

```
csvdiff bin data.csv --column score --boundaries 0 50 100
```

This produces an extra column `score_bin` with values like `0-50`, `50-100`, or `other` for out-of-range entries.

## Options

| Option | Description |
|---|---|
| `--column` | Numeric column to bin (required) |
| `--boundaries N [N ...]` | Ordered boundary values — at least two required |
| `--labels L [L ...]` | Custom labels; must be `len(boundaries) - 1` |
| `--bin-column` | Name for the new bin column (default: `<column>_bin`) |
| `--out-of-range` | Label for values outside all bins (default: `other`) |
| `--format` | Output format: `csv` (default), `json`, or `stats` |

## Examples

### Custom labels

```
csvdiff bin grades.csv --column mark --boundaries 0 40 70 100 \
  --labels fail pass distinction
```

### Stats summary

```
csvdiff bin sales.csv --column revenue --boundaries 0 1000 5000 \
  --format stats
```

Output:

```
0-1000: 42
1000-5000: 18
other: 3
```

## Python API

```python
from csvdiff.binner import bin_column

result = bin_column(
    rows,
    column="revenue",
    boundaries=[0, 1000, 5000],
    labels=["small", "large"],
)
print(result.bin_counts)
```

`bin_column` returns a `BinResult` with:

- `rows` — original rows with the new bin column appended
- `headers` — updated header list
- `bin_counts` — mapping of label → row count
- `boundaries`, `labels`, `bin_column` — configuration echo
