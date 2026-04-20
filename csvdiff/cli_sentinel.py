"""CLI sub-command: sentinel — flag rows that violate alert rules."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import List

from csvdiff.sentinel import SentinelError, sentinel


def _read_csv(path: str) -> List[dict]:
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)


def _write_csv(rows, path: str) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def cmd_sentinel(args: argparse.Namespace) -> int:
    rows = _read_csv(args.file)

    rules = {}
    for spec in args.rule or []:
        if ":" not in spec:
            print(f"error: invalid rule spec {spec!r} — expected column:rule", file=sys.stderr)
            return 2
        col, rule = spec.split(":", 1)
        rules[col] = rule

    label_col = getattr(args, "label_column", None)

    try:
        result = sentinel(rows, rules, label_column=label_col)
    except SentinelError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        out = {
            "match_count": result.match_count,
            "flagged_rows": result.flagged_row_count,
            "matches": [
                {"column": m.column, "rule": m.rule, "value": m.value}
                for m in result.matches
            ],
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"Matches : {result.match_count}")
        print(f"Flagged rows: {result.flagged_row_count}")
        for m in result.matches:
            print(f"  [{m.rule}] column={m.column!r} value={m.value!r}")

    if args.output:
        _write_csv(result.rows, args.output)

    return 1 if result.match_count > 0 else 0


def _add_sentinel_parser(sub) -> None:
    p = sub.add_parser("sentinel", help="flag rows violating alert rules")
    p.add_argument("file", help="input CSV file")
    p.add_argument(
        "--rule", metavar="COL:RULE", action="append",
        help="column:rule pair; repeatable (rules: nonempty, numeric, positive, negative)",
    )
    p.add_argument("--label-column", metavar="COL", dest="label_column",
                   help="add a column with triggered rule names")
    p.add_argument("--output", "-o", metavar="FILE", help="write annotated CSV here")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=cmd_sentinel)


def build_sentinel_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff sentinel")
    sub = parser.add_subparsers()
    _add_sentinel_parser(sub)
    return parser
