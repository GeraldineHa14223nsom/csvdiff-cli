"""Classify rows into categories based on column value patterns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


class ClassifierError(Exception):
    def __str__(self) -> str:
        return f"ClassifierError: {self.args[0]}"


@dataclass
class ClassifyResult:
    rows: List[Dict[str, str]]
    label_column: str
    rules: List[Dict]
    classified_count: int = 0
    unmatched_count: int = 0


def _validate(column: str, rules: List[Dict], rows: List[Dict[str, str]]) -> None:
    if not rules:
        raise ClassifierError("At least one rule must be provided.")
    if rows and column not in rows[0]:
        raise ClassifierError(f"Column '{column}' not found in rows.")
    for rule in rules:
        if "label" not in rule:
            raise ClassifierError("Each rule must have a 'label' key.")
        if "pattern" not in rule and "range" not in rule:
            raise ClassifierError("Each rule must have a 'pattern' or 'range' key.")


def _match_rule(value: str, rule: Dict) -> bool:
    if "pattern" in rule:
        return bool(re.search(rule["pattern"], value, re.IGNORECASE))
    if "range" in rule:
        try:
            num = float(value)
            lo, hi = rule["range"]
            return lo <= num <= hi
        except (ValueError, TypeError):
            return False
    return False


def classify(
    rows: List[Dict[str, str]],
    column: str,
    rules: List[Dict],
    label_column: str = "label",
    default_label: Optional[str] = None,
) -> ClassifyResult:
    """Classify each row by matching *column* against ordered *rules*."""
    _validate(column, rules, rows)
    out: List[Dict[str, str]] = []
    classified = 0
    unmatched = 0
    for row in rows:
        value = row.get(column, "")
        matched_label: Optional[str] = None
        for rule in rules:
            if _match_rule(value, rule):
                matched_label = rule["label"]
                break
        if matched_label is not None:
            classified += 1
        else:
            matched_label = default_label
            unmatched += 1
        out.append({**row, label_column: matched_label or ""})
    return ClassifyResult(
        rows=out,
        label_column=label_column,
        rules=rules,
        classified_count=classified,
        unmatched_count=unmatched,
    )
