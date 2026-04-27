# HTML Export

The `html` sub-command renders the diff between two CSV files as a
self-contained HTML page.

## Usage

```
csvdiff html LEFT RIGHT [options]
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--keys COL …` | *(none)* | Key column(s) used to match rows |
| `--title TEXT` | `CSV Diff Report` | `<title>` of the HTML page |
| `--max-rows N` | `200` | Maximum rows shown per category |
| `--show-unchanged` | off | Include unchanged rows in the table |
| `-o / --output FILE` | stdout | Write HTML to a file instead of stdout |

## Row categories

Each `<tr>` element is annotated with a CSS class so you can apply custom
styling:

| Class | Meaning |
|---|---|
| `csvdiff-added` | Row present only in the right file |
| `csvdiff-removed` | Row present only in the left file |
| `csvdiff-modified` | Row present in both files but with changed values |
| `csvdiff-unchanged` | Row identical in both files (hidden by default) |

## Examples

```bash
# Write report to stdout
csvdiff html old.csv new.csv --keys id

# Save to a file with a custom title
csvdiff html old.csv new.csv --keys id --title "Daily Diff" -o report.html

# Include unchanged rows and limit to 50 rows per section
csvdiff html old.csv new.csv --show-unchanged --max-rows 50 -o full.html
```

## Python API

```python
from csvdiff.core import diff
from csvdiff.formatter_html import HtmlOptions, format_html

result = diff("old.csv", "new.csv", key_columns=["id"])
opts = HtmlOptions(title="My Report", show_unchanged=True)
html = format_html(result, opts)
print(html)
```
