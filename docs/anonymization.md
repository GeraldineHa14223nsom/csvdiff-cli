# Anonymization

The `anonymize` command replaces sensitive column values with hashed or masked alternatives.

## Usage

```
csvdiff anonymize <file> --columns COL [COL ...] [options]
```

## Methods

### Hash (default)

Replaces each value with a 16-character SHA-256 hex digest.

```bash
csvdiff anonymize users.csv --columns email name
```

Add a salt to make hashes unpredictable:

```bash
csvdiff anonymize users.csv --columns email --salt mysecret
```

### Mask

Replaces characters with a mask character (`*` by default).

```bash
csvdiff anonymize users.csv --columns email --method mask
```

Keep a prefix visible with `--keep`:

```bash
csvdiff anonymize users.csv --columns name --method mask --keep 2
# Alice -> Al***
```

Custom mask character:

```bash
csvdiff anonymize users.csv --columns name --method mask --mask-char X
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--columns` | required | Columns to anonymize |
| `--method` | `hash` | `hash` or `mask` |
| `--salt` | `` | Salt string for hashing |
| `--mask-char` | `*` | Replacement character for masking |
| `--keep` | `0` | Characters to preserve at the start |

## Output

The anonymized CSV is written to stdout, preserving all other columns unchanged.
