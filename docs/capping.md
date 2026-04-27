# Row Capping

The **capper** module limits the number of rows returned per group,
identified by a configurable key column.  This is useful when you want
a representative sample from each category without loading the full
dataset.

## API

```python
from csvdiff.capper import cap_rows, CapResult

rows = [
    {"dept": "eng",   "name": "Alice"},
    {"dept": "eng",   "name": "Bob"},
    {"dept": "eng",   "name": "Carol"},
    {"dept": "hr",    "name": "Dave"},
    {"dept": "sales", "name": "Frank"},
]

result: CapResult = cap_rows(rows, column="dept", cap=2)
```

### `CapResult` attributes

| Attribute        | Type              | Description                                      |
|------------------|-------------------|--------------------------------------------------|
| `rows`           | `list[dict]`      | Rows that survived the cap                       |
| `original_count` | `int`             | Total input rows                                 |
| `capped_count`   | `int`             | Rows kept after applying the cap                 |
| `removed_count`  | `int` (property)  | `original_count - capped_count`                  |
| `group_column`   | `str`             | Column used for grouping                         |
| `cap`            | `int`             | Maximum rows allowed per group                   |
| `group_sizes`    | `dict[str, int]`  | Original row count per group key (before capping)|

## Errors

`CapperError` is raised when:

- `cap < 1`
- The specified `column` does not exist in the row headers

## Notes

- Row order is preserved; the **first** `cap` rows for each group value
  are kept and the rest discarded.
- An empty input list is handled gracefully and returns an empty
  `CapResult`.
