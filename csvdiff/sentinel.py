"""Sentinel: detect and flag rows matching a set of alert conditions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class SentinelError(Exception):
    def __str__(self) -> str:  # pragma: no cover
        return self.args[0]


@dataclass
class SentinelMatch:
    row: Dict[str, str]
    column: str
    rule: str
    value: str


@dataclass
class SentinelResult:
    rows: List[Dict[str, str]]
    matches: List[SentinelMatch] = field(default_factory=list)

    @property
    def match_count(self) -> int:
        return len(self.matches)

    @property
    def flagged_row_count(self) -> int:
        return len({id(m.row) for m in self.matches})


def _get_checker(rule: str):
    """Return a callable(value) -> bool for the named rule."""
    if rule == "nonempty":
        return lambda v: v.strip() == ""
    if rule == "numeric":
        return lambda v: v.strip() != "" and not _is_numeric(v)
    if rule == "positive":
        return lambda v: _is_numeric(v) and float(v) <= 0
    if rule == "negative":
        return lambda v: _is_numeric(v) and float(v) >= 0
    raise SentinelError(f"Unknown sentinel rule: {rule!r}")


def _is_numeric(v: str) -> bool:
    try:
        float(v)
        return True
    except ValueError:
        return False


def sentinel(
    rows: List[Dict[str, str]],
    rules: Dict[str, str],
    label_column: Optional[str] = None,
) -> SentinelResult:
    """Flag rows where column values violate the given rules.

    Args:
        rows: input rows.
        rules: mapping of column -> rule name.
        label_column: if set, add a column with the triggered rule name.
    """
    if not rows:
        return SentinelResult(rows=[], matches=[])

    headers = list(rows[0].keys())
    for col in rules:
        if col not in headers:
            raise SentinelError(f"Column {col!r} not found in data")

    checkers = {col: _get_checker(rule) for col, rule in rules.items()}
    matches: List[SentinelMatch] = []
    out_rows: List[Dict[str, str]] = []

    for row in rows:
        triggered = []
        for col, check in checkers.items():
            if check(row.get(col, "")):
                m = SentinelMatch(row=row, column=col, rule=rules[col], value=row.get(col, ""))
                matches.append(m)
                triggered.append(rules[col])
        if label_column is not None:
            new_row = dict(row)
            new_row[label_column] = ",".join(triggered) if triggered else ""
            out_rows.append(new_row)
        else:
            out_rows.append(dict(row))

    return SentinelResult(rows=out_rows, matches=matches)
