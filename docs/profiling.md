# Column Profiling

The `profile` sub-command analyses every column in a CSV file and reports
key statistics — useful for data-quality checks before running a diff.

## Usage

```
csvdiff profile <file> [--format text|json] [--sample-size N]
```

### Arguments

| Argument | Default | Description |
|---|---|---|
| `file` | *(required)* | Path to the CSV file to profile |
| `--format` | `text` | Output format: `text` or `json` |
| `--sample-size` | `5` | Number of example values to include per column |

## Output fields

| Field | Description |
|---|---|
| `count` | Total number of rows |
| `non_empty` | Rows where the value is not blank |
| `empty_count` | Rows where the value is blank |
| `fill_rate` | `non_empty / count` (0.0 – 1.0) |
| `unique_values` | Number of distinct values seen |
| `min_length` | Shortest string length observed |
| `max_length` | Longest string length observed |
| `sample_values` | Up to `--sample-size` example values |

## Examples

```bash
# Human-readable summary
csvdiff profile data.csv

# Machine-readable JSON
csvdiff profile data.csv --format json

# Larger sample of values
csvdiff profile data.csv --sample-size 10
```

### Sample text output

```
id: count=100, non_empty=100, fill_rate=100.0%, unique=100, min_len=1, max_len=3
name: count=100, non_empty=98, fill_rate=98.0%, unique=67, min_len=3, max_len=20
```

### Sample JSON output

```json
[
  {
    "column": "id",
    "count": 100,
    "non_empty": 100,
    "empty_count": 0,
    "fill_rate": 1.0,
    "unique_values": 100,
    "min_length": 1,
    "max_length": 3,
    "sample_values": ["1", "2", "3", "4", "5"]
  }
]
```
