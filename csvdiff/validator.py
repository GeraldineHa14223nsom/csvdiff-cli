"""Row-level validation for CSV data against simple rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


class ValidationError(Exception):
    def __str__(self) -> str:
        return self.args[0]


@dataclass
class RuleViolation:
    row_index: int
    column: str
    rule: str
    value: str


@dataclass
class ValidationResult:
    violations: List[RuleViolation] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.violations) == 0

    def violation_count(self) -> int:
        return len(self.violations)


Rule = Callable[[str], bool]

_BUILTIN_RULES: Dict[str, Rule] = {
    "nonempty": lambda v: v.strip() != "",
    "numeric": lambda v: v.strip().lstrip("-").replace(".", "", 1).isdigit(),
    "integer": lambda v: v.strip().lstrip("-").isdigit(),
    "ascii": lambda v: v.isascii(),
}


def get_rule(name: str) -> Rule:
    """Return a built-in rule callable by name."""
    if name not in _BUILTIN_RULES:
        raise ValidationError(
            f"Unknown rule '{name}'. Available: {sorted(_BUILTIN_RULES)}"
        )
    return _BUILTIN_RULES[name]


def validate_rows(
    rows: List[Dict[str, str]],
    rules: Dict[str, List[str]],
    columns: Optional[List[str]] = None,
) -> ValidationResult:
    """Validate *rows* against *rules* mapping column -> [rule_names].

    Args:
        rows: list of row dicts.
        rules: mapping of column name to list of rule names to apply.
        columns: if given, restrict validation to these columns only.

    Returns:
        ValidationResult containing any violations found.
    """
    result = ValidationResult()
    active_rules: Dict[str, List[str]] = {
        col: names
        for col, names in rules.items()
        if columns is None or col in columns
    }
    compiled: Dict[str, List[tuple[str, Rule]]] = {
        col: [(name, get_rule(name)) for name in names]
        for col, names in active_rules.items()
    }
    for idx, row in enumerate(rows):
        for col, rule_pairs in compiled.items():
            value = row.get(col, "")
            for rule_name, fn in rule_pairs:
                if not fn(value):
                    result.violations.append(
                        RuleViolation(
                            row_index=idx,
                            column=col,
                            rule=rule_name,
                            value=value,
                        )
                    )
    return result
