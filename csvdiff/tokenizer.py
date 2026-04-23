"""Tokenize CSV column values into word/token frequency tables."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Sequence


class TokenizerError(Exception):
    def __str__(self) -> str:
        return f"TokenizerError: {self.args[0]}"


@dataclass
class TokenResult:
    column: str
    total_rows: int
    token_counts: Dict[str, int]
    vocabulary_size: int

    def top_n(self, n: int = 10) -> List[tuple]:
        """Return the n most common tokens as (token, count) pairs."""
        return Counter(self.token_counts).most_common(n)

    def frequency(self, token: str) -> float:
        """Return relative frequency of a token (0.0–1.0)."""
        if self.total_rows == 0:
            return 0.0
        return self.token_counts.get(token, 0) / self.total_rows


def _validate(rows: List[dict], column: str) -> None:
    if not rows:
        raise TokenizerError("rows must not be empty")
    if column not in rows[0]:
        raise TokenizerError(f"column '{column}' not found in rows")


def _tokenize_value(value: str, pattern: str) -> List[str]:
    """Split a cell value into tokens using the given regex pattern."""
    return [t.lower() for t in re.split(pattern, value) if t.strip()]


def tokenize(
    rows: List[dict],
    column: str,
    split_pattern: str = r"[\s,;|]+",
    min_length: int = 1,
) -> TokenResult:
    """Tokenize all values in *column* and return a TokenResult.

    Parameters
    ----------
    rows:           Input rows (list of dicts).
    column:         Column whose values should be tokenized.
    split_pattern:  Regex used to split each cell value into tokens.
    min_length:     Minimum token length; shorter tokens are discarded.
    """
    _validate(rows, column)
    if min_length < 1:
        raise TokenizerError("min_length must be >= 1")

    counts: Counter = Counter()
    for row in rows:
        raw = str(row.get(column, "") or "")
        for tok in _tokenize_value(raw, split_pattern):
            if len(tok) >= min_length:
                counts[tok] += 1

    return TokenResult(
        column=column,
        total_rows=len(rows),
        token_counts=dict(counts),
        vocabulary_size=len(counts),
    )
