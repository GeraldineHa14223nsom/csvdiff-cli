# Fuzzy Matching

The `csvdiff fuzzy` feature lets you match rows between two CSV files using
fuzzy string similarity on a chosen key column. This is useful when the same
entity appears with slightly different spellings across datasets.

## How It Works

For each row in the **left** file, `fuzzy_match` finds the best candidate in
the **right** file by computing a similarity score (0.0–1.0) using Python's
`difflib.SequenceMatcher`. A match is accepted when the score meets or exceeds
the configured `threshold`.

Each right-side row can be matched at most once (greedy, highest-score wins).

## API

```python
from csvdiff.fuzzer import fuzzy_match

result = fuzzy_match(
    left_rows,   # list[dict[str, str]]
    right_rows,  # list[dict[str, str]]
    key="name",  # column to compare
    threshold=0.8,
)

print(result.match_count)       # number of accepted matches
print(result.mean_score)        # average similarity of matched pairs
print(result.unmatched_left)    # rows with no suitable right partner
print(result.unmatched_right)   # rows that were never matched
```

## FuzzyResult fields

| Field | Type | Description |
|---|---|---|
| `matches` | `list[FuzzyMatch]` | Accepted match pairs with scores |
| `unmatched_left` | `list[dict]` | Left rows with no match above threshold |
| `unmatched_right` | `list[dict]` | Right rows never selected |
| `match_count` | `int` | `len(matches)` |
| `mean_score` | `float \| None` | Average score, `None` when no matches |

## FuzzyMatch fields

| Field | Description |
|---|---|
| `left_key` | Raw key value from the left row |
| `right_key` | Raw key value from the right row |
| `score` | Similarity score (0.0–1.0, 4 d.p.) |
| `left_row` | Full left row dict |
| `right_row` | Full right row dict |

## Errors

`FuzzerError` is raised when:
- `threshold` is outside `[0.0, 1.0]`
- The specified `key` column is absent from either file's rows

## Threshold guidance

| Threshold | Typical use |
|---|---|
| `1.0` | Exact match only |
| `0.85` | Minor typos / abbreviations |
| `0.7` | Moderate name variations |
| `< 0.6` | Very loose — expect false positives |
