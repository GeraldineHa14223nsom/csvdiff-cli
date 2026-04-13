"""CLI sub-command: validate-rows — check CSV rows against named rules."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import Dict, List

from csvdiff.validator import ValidationError, validate_rows


def _parse_rules(rule_args: List[str]) -> Dict[str, List[str]]:
    """Parse 'column:rule1,rule2' strings into a dict."""
    rules: Dict[str, List[str]] = {}
    for arg in rule_args:
        if ":" not in arg:
            raise argparse.ArgumentTypeError(
                f"Rule '{arg}' must be in 'column:rule' format."
            )
        col, _, names = arg.partition(":")
        rules.setdefault(col, []).extend(names.split(","))
    return rules


def _add_validate_rows_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser(
        "validate-rows",
        help="Validate CSV rows against named rules.",
    )
    p.add_argument("file", help="CSV file to validate.")
    p.add_argument(
        "--rule",
        dest="rules",
        action="append",
        default=[],
        metavar="COL:RULE",
        help="Apply RULE to COL. May be repeated. Rules: nonempty, numeric, integer, ascii.",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    p.set_defaults(func=cmd_validate_rows)


def build_validate_rows_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="csvdiff validate-rows")
    sub = p.add_subparsers()
    _add_validate_rows_parser(sub)
    return p


def cmd_validate_rows(args: argparse.Namespace) -> int:
    try:
        rules = _parse_rules(args.rules)
    except argparse.ArgumentTypeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    try:
        with open(args.file, newline="") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 2

    try:
        result = validate_rows(rows, rules)
    except ValidationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        data = [
            {"row": v.row_index, "column": v.column, "rule": v.rule, "value": v.value}
            for v in result.violations
        ]
        print(json.dumps({"valid": result.is_valid, "violations": data}, indent=2))
    else:
        if result.is_valid:
            print("OK: no violations found.")
        else:
            for v in result.violations:
                print(f"row {v.row_index}: [{v.column}] failed '{v.rule}' (value={v.value!r})")

    return 0 if result.is_valid else 1
