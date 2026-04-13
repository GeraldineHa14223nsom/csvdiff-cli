# Row Sampling

The `sampler` module lets you draw representative samples from a `DiffResult`
without loading every changed row into memory at once.

## Python API

```python
from csvdiff.pipeline import run
from csvdiff.sampler import sample_result, sample_fraction

diff = run("old.csv", "new.csv", key_cols=["id"])

# Fixed-size sample — up to 10 rows per category
sr = sample_result(diff, n=10, seed=42)
print(sr.added)    # list[dict]
print(sr.removed)
print(sr.modified)

# Fraction-based sample — 20 % of each category
sr2 = sample_fraction(diff, frac=0.2, seed=0)
```

### `sample_result` parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `result` | `DiffResult` | — | Diff to sample from |
| `n` | `int` | `10` | Max rows per category |
| `seed` | `int \| None` | `None` | Random seed for reproducibility |
| `include_unchanged` | `bool` | `False` | Also sample unchanged rows |

### `sample_fraction` parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `result` | `DiffResult` | — | Diff to sample from |
| `frac` | `float` | `0.1` | Fraction in `(0, 1]` |
| `seed` | `int \| None` | `None` | Random seed |

## CLI

```
csvdiff sample old.csv new.csv -k id --count 5 --seed 42
csvdiff sample old.csv new.csv -k id --frac 0.1 --format json
csvdiff sample old.csv new.csv -k id --count 20 --include-unchanged
```

### Flags

| Flag | Description |
|------|-------------|
| `-k / --key` | Key column(s) |
| `-n / --count` | Max rows per category (default 10) |
| `--frac` | Fraction mode (overrides `--count`) |
| `--seed` | Integer random seed |
| `--include-unchanged` | Include unchanged rows in output |
| `--format` | `text` (default) or `json` |
