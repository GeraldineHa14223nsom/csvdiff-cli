"""CLI sub-command: aggregate columns from a CSV file."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import List

from csvdiff.aggregator import AggregatorError, aggregate_all


def _add_aggregate_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "aggregate",
        help="Compute numeric statistics for one or more columns in a CSV file.",
    )
    p.add_argument("file", help="Path to the CSV file.")
    p.add_argument(
        "--columns",
        required=True,
        metavar="COL",
        nargs="+",
        help="Column(s) to aggregate.",
    )
    p.add_argument(
        "--format",
        dest="fmt",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    p.set_defaults(func=cmd_aggregate)


def build_aggregate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff aggregate")
    sub = parser.add_subparsers()
    _add_aggregate_parser(sub)
    return parser


def cmd_aggregate(args: argparse.Namespace) -> int:
    try:
        with open(args.file, newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 2

    try:
        results = aggregate_all(rows, args.columns)
    except AggregatorError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.fmt == "json":
        payload = {
            col: {
                "count": r.count,
                "total": r.total,
                "min": r.minimum,
                "max": r.maximum,
                "mean": r.mean,
            }
            for col, r in results.items()
        }
        print(json.dumps(payload, indent=2))
    else:
        for col, r in results.items():
            print(f"[{col}]")
            print(f"  count : {r.count}")
            print(f"  total : {r.total}")
            print(f"  min   : {r.minimum}")
            print(f"  max   : {r.maximum}")
            print(f"  mean  : {r.mean}")
    return 0
