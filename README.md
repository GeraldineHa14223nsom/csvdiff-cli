# csvdiff-cli

A command-line tool for diffing and reconciling large CSV files with configurable key columns and output formats.

---

## Installation

```bash
pip install csvdiff-cli
```

Or install from source:

```bash
git clone https://github.com/yourname/csvdiff-cli.git
cd csvdiff-cli
pip install .
```

---

## Usage

```bash
csvdiff [OPTIONS] FILE_A FILE_B
```

### Options

| Flag | Description |
|------|-------------|
| `-k, --key COLUMN` | Column(s) to use as the primary key (repeatable) |
| `-o, --output FORMAT` | Output format: `text`, `json`, or `csv` (default: `text`) |
| `--ignore COLUMN` | Column(s) to exclude from comparison |
| `--added` | Show only added rows |
| `--removed` | Show only removed rows |
| `--changed` | Show only changed rows |

### Example

```bash
csvdiff -k id -k email --output json old_users.csv new_users.csv
```

This compares `old_users.csv` and `new_users.csv` using `id` and `email` as composite keys and outputs the diff as JSON.

```bash
# Reconcile and write merged output
csvdiff -k id --output csv old_data.csv new_data.csv > reconciled.csv
```

---

## Output

By default, `csvdiff-cli` prints a human-readable summary of added, removed, and changed rows. Use `--output json` for machine-readable output or `--output csv` to produce a reconciled file.

---

## Requirements

- Python 3.8+
- No external dependencies (uses standard library only)

---

## License

This project is licensed under the [MIT License](LICENSE).