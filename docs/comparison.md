# Column Comparison

The `comparer` module lets you compare two CSV datasets column-by-column, with optional numeric tolerance.

## Basic Usage

```python
from csvdiff.comparer import compare, mismatch_count, match_rate

left  = [{"id": "1", "price": "9.99"}, {"id": "2", "price": "4.50"}]
right = [{"id": "1", "price": "9.99"}, {"id": "2", "price": "4.75"}]

result = compare(left, right, columns=["price"])
print(mismatch_count(result))  # 1
print(match_rate(result))      # 0.5
```

## Numeric Tolerance

Floating-point values can be compared with a tolerance threshold:

```python
result = compare(left, right, columns=["price"], tolerance=0.30)
print(mismatch_count(result))  # 0  — diff of 0.25 is within tolerance
```

## CompareResult Fields

| Field | Description |
|---|---|
| `rows` | All compared rows with `_left`, `_right`, and `_match` suffixed columns |
| `mismatches` | Subset of rows where at least one column did not match |
| `columns_compared` | The list of columns that were evaluated |

## Errors

- `ComparerError` is raised if `columns` is empty or contains names not present in the data.
- Rows are compared positionally; the shorter list determines the comparison length.
