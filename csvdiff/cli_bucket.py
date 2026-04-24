"""CLI subcommand: bucket — assign rows to named numeric ranges."""
from __future__ import annotations

import csv
import json
import sys
from argparse import ArgumentParser, Namespace
from typing import List

from csvdiff.bucketer import BucketerError, bucket_rows


def _read_csv(path: str) -> tuple:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        headers = list(reader.fieldnames or [])
    return headers, rows


def _write_csv(rows: list, headers: list, dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)


def _parse_buckets(specs: List[str]) -> list:
    """Parse 'label:low:high' strings into (label, float, float) tuples."""
    result = []
    for spec in specs:
        parts = spec.split(":")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid bucket spec '{spec}'. Expected 'label:low:high'."
            )
        label, low, high = parts
        result.append((label, float(low), float(high)))
    return result


def cmd_bucket(args: Namespace) -> int:
    try:
        _, rows = _read_csv(args.file)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        buckets = _parse_buckets(args.bucket)
        result = bucket_rows(
            rows,
            column=args.column,
            buckets=buckets,
            label_column=args.label_column,
            default_label=args.default_label,
        )
    except (BucketerError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps({"rows": result.rows, "bucket_counts": result.bucket_counts}))
    else:
        if args.output:
            with open(args.output, "w", newline="", encoding="utf-8") as fh:
                _write_csv(result.rows, result.headers, fh)
        else:
            _write_csv(result.rows, result.headers, sys.stdout)

    return 0


def _add_bucket_parser(subparsers) -> None:
    p: ArgumentParser = subparsers.add_parser(
        "bucket", help="Assign rows to named numeric ranges."
    )
    p.add_argument("file", help="Input CSV file.")
    p.add_argument("--column", required=True, help="Numeric column to bucket.")
    p.add_argument(
        "--bucket",
        metavar="LABEL:LOW:HIGH",
        action="append",
        default=[],
        help="Bucket definition (repeatable).",
    )
    p.add_argument("--label-column", default="bucket", help="Name of the new label column.")
    p.add_argument("--default-label", default="other", help="Label for out-of-range values.")
    p.add_argument("--output", "-o", default=None, help="Write output to file instead of stdout.")
    p.add_argument("--format", choices=["csv", "json"], default="csv")
    p.set_defaults(func=cmd_bucket)


def build_bucket_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="csvdiff bucket")
    subs = parser.add_subparsers()
    _add_bucket_parser(subs)
    return parser
