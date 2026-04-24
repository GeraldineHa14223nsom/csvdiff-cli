# Row Tagging

The `tag` module lets you annotate each row with a label that indicates whether
a specified column's value belongs to a predefined set.

## Usage

```bash
csvdiff tag data.csv --column country --values "US,GB" --tag-column region_flag \
    --match-label included --no-match-label excluded
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--column` | *(required)* | Column whose value is tested |
| `--values` | *(required)* | Comma-separated set of match values |
| `--tag-column` | `tag` | Name of the new column added to each row |
| `--match-label` | `match` | Label written when the value is in the set |
| `--no-match-label` | *(empty string)* | Label written when the value is **not** in the set |
| `--output` / `-o` | stdout | Write result to a file instead of stdout |

## Python API

```python
from csvdiff.tagger import tag_rows

rows = [
    {"id": "1", "country": "US"},
    {"id": "2", "country": "DE"},
]

result = tag_rows(
    rows,
    column="country",
    values={"US", "GB"},
    tag_column="flag",
    match_label="tier1",
    no_match_label="other",
)

print(result.tagged_count)    # 1
print(result.untagged_count)  # 1
print(result.rows[0]["flag"]) # "tier1"
print(result.rows[1]["flag"]) # "other"
```

## TagResult fields

| Field | Type | Description |
|---|---|---|
| `headers` | `List[str]` | Column names including the new tag column |
| `rows` | `List[Dict]` | All rows with the tag column appended |
| `tag_column` | `str` | Name of the tag column |
| `tagged_count` | `int` | Number of rows whose value matched |
| `untagged_count` | `int` | Number of rows whose value did not match |

## Errors

- `TaggerError` is raised if the source column does not exist.
- `TaggerError` is raised if the tag column name already exists in the data.
