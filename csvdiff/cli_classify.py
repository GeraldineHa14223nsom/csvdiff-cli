"""CLI command: csvdiff classify — classify rows by column patterns."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import List

from csvdiff.classifier import classify, ClassifierError


def _read_csv(path: str) -> tuple:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        headers = list(reader.fieldnames or [])
    return rows, headers


def _write_csv(rows, out):
    if not rows:
        return
    writer = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def _parse_rules(specs: List[str]) -> List[dict]:
    """Parse rules of the form 'label:pattern' or 'label:lo-hi'."""
    rules = []
    for spec in specs:
        if ":" not in spec:
            raise argparse.ArgumentTypeError(f"Invalid rule spec: {spec!r}")
        label, rest = spec.split(":", 1)
        if "-" in rest and not rest.startswith("^"):
            parts = rest.split("-", 1)
            try:
                lo, hi = float(parts[0]), float(parts[1])
                rules.append({"label": label, "range": [lo, hi]})
                continue
            except ValueError:
                pass
        rules.append({"label": label, "pattern": rest})
    return rules


def cmd_classify(args: argparse.Namespace) -> int:
    try:
        rows, _ = _read_csv(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2

    try:
        rules = _parse_rules(args.rule)
        result = classify(
            rows,
            column=args.column,
            rules=rules,
            label_column=args.label_column,
            default_label=args.default,
        )
    except ClassifierError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.format == "json":
        json.dump(result.rows, sys.stdout, indent=2)
        print()
    else:
        _write_csv(result.rows, sys.stdout)

    if not args.quiet:
        print(
            f"# classified={result.classified_count} unmatched={result.unmatched_count}",
            file=sys.stderr,
        )
    return 0


def _add_classify_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("classify", help="Classify rows by column value patterns")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("--column", required=True, help="Column to match against")
    p.add_argument("--rule", metavar="LABEL:PATTERN", action="append", default=[], required=True)
    p.add_argument("--label-column", default="label", help="Name of the new label column")
    p.add_argument("--default", default=None, help="Label for unmatched rows")
    p.add_argument("--format", choices=["csv", "json"], default="csv")
    p.add_argument("--quiet", action="store_true")
    p.set_defaults(func=cmd_classify)


def build_classify_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff-classify")
    sub = parser.add_subparsers(dest="command")
    _add_classify_parser(sub)
    return parser
