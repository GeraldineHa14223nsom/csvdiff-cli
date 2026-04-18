# Column Correlation

The `correlator` module computes pairwise **Pearson correlation coefficients**
between numeric columns in a CSV dataset.

## Usage

```python
from csvdiff.correlator import correlate

rows = [
    {"x": "1", "y": "2"},
    {"x": "2", "y": "4"},
    {"x": "3", "y": "6"},
]

result = correlate(rows, columns=["x", "y"])
print(result.matrix["x"]["y"])  # 1.0
```

## API

### `correlate(rows, columns) -> CorrelationResult`

| Parameter | Type | Description |
|-----------|------|-------------|
| `rows` | `Sequence[Dict[str, str]]` | CSV rows as dicts |
| `columns` | `List[str]` | Column names to correlate (≥ 2) |

### `CorrelationResult`

| Attribute | Type | Description |
|-----------|------|-------------|
| `columns` | `List[str]` | Columns included in the analysis |
| `matrix` | `Dict[str, Dict[str, float]]` | Symmetric correlation matrix |

## Notes

- All specified columns must contain numeric values.
- A constant column (zero variance) yields `nan` for its correlations.
- Requires at least 2 rows and 2 columns.
- Coefficients are rounded to 6 decimal places.
