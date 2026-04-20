# Sentinel — Row Alert Detection

The `sentinel` module scans CSV rows and flags any that violate a set of
configurable alert rules. It is useful for data-quality monitoring pipelines
where you want to surface bad data before it reaches downstream systems.

## Supported Rules

| Rule | Triggers when … |
|------|-----------------|
| `nonempty` | the cell is blank or whitespace-only |
| `numeric` | the cell is non-blank but cannot be parsed as a number |
| `positive` | the numeric value is ≤ 0 |
| `negative` | the numeric value is ≥ 0 |

## Python API

```python
from csvdiff.sentinel import sentinel

rows = [
    {"id": "1", "name": "Alice", "score": "42"},
    {"id": "2", "name": "",      "score": "-5"},
]

result = sentinel(rows, rules={"name": "nonempty", "score": "positive"})
print(result.match_count)       # 2
print(result.flagged_row_count) # 2
for m in result.matches:
    print(m.column, m.rule, m.value)
```

### Label column

Pass `label_column="_flag"` to annotate each output row with the names of
any triggered rules (comma-separated), or an empty string for clean rows:

```python
result = sentinel(rows, rules={"score": "positive"}, label_column="_flag")
for row in result.rows:
    print(row["_flag"])  # "positive" or ""
```

## CLI

```
csvdiff sentinel data.csv \
    --rule name:nonempty \
    --rule score:positive \
    --label-column _flag \
    --output annotated.csv \
    --format text
```

Exit codes:

- **0** — no rule violations found
- **1** — one or more violations detected
- **2** — usage error (bad rule spec, unknown column, missing file)

### JSON output

```json
{
  "match_count": 2,
  "flagged_rows": 2,
  "matches": [
    {"column": "name",  "rule": "nonempty", "value": ""},
    {"column": "score", "rule": "positive",  "value": "-5"}
  ]
}
```
