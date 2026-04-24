# Table Format Output

`csvdiff` can render diff results as a human-readable ASCII table, making it
easy to inspect changes at a glance in a terminal.

## Usage

Pass `--format table` to any diff command:

```bash
csvdiff diff left.csv right.csv --key id --format table
```

Sample output:

```
[ADDED]
 id | name
----+-------
 3  | Carol

[REMOVED]
 id | name
----+-----
 2  | Bob

[MODIFIED]
 id | name
----+--------
 1  | Alicia
```

## Options

| Option | Default | Description |
|---|---|---|
| `max_col_width` | `24` | Maximum characters per cell before truncation |
| `show_unchanged` | `False` | Include an `[UNCHANGED]` section for unmodified rows |
| `separator` | `\|` | Column separator character |

## Python API

```python
from csvdiff.formatter_table import format_table, TableOptions
from csvdiff.core import diff

result = diff(left_rows, right_rows, key_columns=["id"])
opts = TableOptions(max_col_width=30, show_unchanged=True)
print(format_table(result, opts))
```

## Truncation

Cell values longer than `max_col_width` are truncated with a `…` suffix so
that the table stays readable in narrow terminals.  The original data is never
modified — truncation is display-only.

## Empty Diffs

When there are no differences the output is simply:

```
(no differences)
```
