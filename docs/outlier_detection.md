# Outlier Detection

`csvdiff` can flag rows whose numeric values are statistically unusual.

## Methods

### Z-Score

Marks a value as an outlier when its distance from the column mean exceeds
`threshold` standard deviations (default **3.0**).

```
csvdiff outlier data.csv price --method zscore --threshold 3.0
```

### IQR (Interquartile Range)

Marks a value as an outlier when it falls below `Q1 - threshold * IQR` or
above `Q3 + threshold * IQR` (default threshold **1.5**).

```
csvdiff outlier data.csv price --method iqr --threshold 1.5
```

## Output formats

**Text** (default)

```
Column   : price
Method   : zscore
Threshold: 3.0
Total    : 500
Outliers : 3

Outlier rows:
  id=42, price=99999
  ...
```

**JSON**

```
csvdiff outlier data.csv price --format json
```

```json
{
  "column": "price",
  "method": "zscore",
  "threshold": 3.0,
  "total_rows": 500,
  "outlier_count": 3,
  "outlier_rows": [{"id": "42", "price": "99999"}]
}
```

## Python API

```python
from csvdiff.outlier import detect_outliers

result = detect_outliers(rows, column="price", method="iqr", threshold=1.5)
print(result.outlier_count())
for row in result.outlier_rows:
    print(row)
```
