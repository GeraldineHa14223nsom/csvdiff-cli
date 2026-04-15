# Column Flattening

The `flatten` command expands a column that contains JSON object strings into
multiple individual columns — one per key in the JSON object.

## Usage

```
csvdiff flatten <file> <column> [options]
```

### Arguments

| Argument | Description |
|---|---|
| `file` | Path to the input CSV file |
| `column` | Name of the column holding JSON objects |

### Options

| Flag | Description |
|---|---|
| `--prefix TEXT` | Prefix to prepend to every new column name |
| `--drop-source` | Remove the source JSON column from the output |
| `-o / --output PATH` | Write result to file instead of stdout |
| `-v / --verbose` | Print a summary line to stderr |

## Example

Given `data.csv`:

```
id,name,meta
1,Alice,"{""age"": 30, ""city"": ""NY""}"
2,Bob,"{""age"": 25, ""city"": ""LA""}"
```

Running:

```bash
csvdiff flatten data.csv meta --prefix meta_ --drop-source -o out.csv
```

Produces `out.csv`:

```
id,name,meta_age,meta_city
1,Alice,30,NY
2,Bob,25,LA
```

## Notes

- Rows where the JSON column is not a valid JSON object receive empty strings
  for all new columns.
- Column order: original columns first (minus the source if `--drop-source` is
  set), then new columns in the order they were first encountered.
- Nested objects are **not** recursively flattened; only the top-level keys are
  expanded.
