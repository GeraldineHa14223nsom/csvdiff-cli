# Row Classification

The `classify` module assigns a label to each row based on ordered matching rules
applied to a chosen column.

## Overview

Rules are evaluated in order; the first matching rule wins.  Each rule is either
a **regex pattern** match or a **numeric range** match.

## Python API

```python
from csvdiff.classifier import classify

rows = [
    {"product": "Widget A", "price": "12.50"},
    {"product": "Gadget B", "price": "149.99"},
    {"product": "Doohickey", "price": "5.00"},
]

rules = [
    {"label": "budget",   "range": [0, 20]},
    {"label": "premium",  "range": [21, 999]},
]

result = classify(rows, column="price", rules=rules, default_label="unknown")
for r in result.rows:
    print(r["product"], "->", r["label"])
```

Output:

```
Widget A -> budget
Gadget B -> premium
Doohickey -> budget
```

## ClassifyResult fields

| Field | Type | Description |
|---|---|---|
| `rows` | list[dict] | Original rows with the new label column appended |
| `label_column` | str | Name of the label column (default `"label"`) |
| `rules` | list[dict] | Rules used for classification |
| `classified_count` | int | Rows matched by at least one rule |
| `unmatched_count` | int | Rows that fell through to the default |

## Rule format

### Pattern rule

```python
{"label": "my_label", "pattern": r"regex_here"}
```

Matching is case-insensitive via `re.IGNORECASE`.

### Range rule

```python
{"label": "my_label", "range": [low, high]}  # inclusive on both ends
```

Non-numeric values silently fail to match the rule.

## CLI usage

```bash
csvdiff classify data.csv \
    --column price \
    --rule budget:0-20 \
    --rule premium:21-999 \
    --default unknown \
    --label-column tier
```

Use `--format json` for JSON output.
