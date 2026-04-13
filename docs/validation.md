# Row Validation

The `validate-rows` sub-command lets you check every row in a CSV file against
a set of named rules. This is useful for catching data-quality issues before
or after a diff/reconcile step.

## Usage

```
csvdiff validate-rows <file> [--rule COL:RULE ...] [--format text|json]
```

### Arguments

| Argument | Description |
|---|---|
| `file` | Path to the CSV file to validate. |
| `--rule COL:RULE` | Apply `RULE` to column `COL`. Repeat for multiple rules. |
| `--format` | Output format: `text` (default) or `json`. |

## Built-in Rules

| Rule | Description |
|---|---|
| `nonempty` | Value must not be blank or whitespace-only. |
| `numeric` | Value must be parseable as a number (int or float). |
| `integer` | Value must be a whole number (no decimal point). |
| `ascii` | Value must contain only ASCII characters. |

## Examples

### Text output (default)

```bash
csvdiff validate-rows data.csv --rule name:nonempty --rule age:integer
```

On success:
```
OK: no violations found.
```

On failure:
```
row 3: [age] failed 'integer' (value='n/a')
row 7: [name] failed 'nonempty' (value='')
```

### JSON output

```bash
csvdiff validate-rows data.csv --rule price:numeric --format json
```

```json
{
  "valid": false,
  "violations": [
    {"row": 2, "column": "price", "rule": "numeric", "value": "free"}
  ]
}
```

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | All rows passed validation. |
| `1` | One or more violations found. |
| `2` | Usage error (bad argument, missing file, unknown rule). |

## Programmatic API

```python
from csvdiff.validator import validate_rows

rows = [{"name": "Alice", "age": "30"}, {"name": "", "age": "bad"}]
result = validate_rows(rows, {"name": ["nonempty"], "age": ["integer"]})
print(result.is_valid)          # False
print(result.violation_count()) # 2
```
