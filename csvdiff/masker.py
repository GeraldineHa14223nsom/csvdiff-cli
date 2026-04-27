"""masker.py – mask (redact) values in specified CSV columns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


class MaskerError(Exception):
    def __str__(self) -> str:  # pragma: no cover
        return f"MaskerError: {self.args[0]}"


@dataclass
class MaskResult:
    rows: List[Dict[str, str]]
    headers: List[str]
    masked_columns: List[str]
    masked_count: int

    @property
    def row_count(self) -> int:
        return len(self.rows)


def _validate(columns: List[str], headers: List[str]) -> None:
    unknown = [c for c in columns if c not in headers]
    if unknown:
        raise MaskerError(
            f"column(s) not found in data: {', '.join(unknown)}"
        )


def mask(
    rows: List[Dict[str, str]],
    columns: List[str],
    *,
    mask_char: str = "*",
    mask_length: int = 6,
    partial: bool = False,
    visible_chars: int = 2,
) -> MaskResult:
    """Return a new list of rows with *columns* redacted.

    Parameters
    ----------
    rows:          Input rows (list of dicts).
    columns:       Column names to mask.
    mask_char:     Character used for masking (default ``'*'``).
    mask_length:   Fixed length of the mask when *partial* is False.
    partial:       When True, keep the first *visible_chars* characters and
                   replace the rest with *mask_char* repeated to fill the
                   original value length.
    visible_chars: Number of leading characters to preserve in partial mode.
    """
    if not rows:
        return MaskResult(
            rows=[], headers=[], masked_columns=list(columns), masked_count=0
        )

    headers = list(rows[0].keys())
    _validate(columns, headers)
    col_set = set(columns)
    masked_count = 0
    out: List[Dict[str, str]] = []

    for row in rows:
        new_row = dict(row)
        for col in col_set:
            original = row.get(col, "")
            if original:
                if partial:
                    keep = original[:visible_chars]
                    hidden_len = max(len(original) - visible_chars, 0)
                    new_row[col] = keep + mask_char * hidden_len
                else:
                    new_row[col] = mask_char * mask_length
                masked_count += 1
        out.append(new_row)

    return MaskResult(
        rows=out,
        headers=headers,
        masked_columns=list(columns),
        masked_count=masked_count,
    )
