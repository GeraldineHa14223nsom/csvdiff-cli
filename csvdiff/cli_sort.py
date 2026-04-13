"""CLI sub-command: csvdiff sort — sort a CSV file by one or more columns."""

from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from csvdiff.sorter import SortError, sort_rows


def _add_sort_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "sort",
        help="Sort a CSV file by one or more columns.",
    )
    p.add_argument("file", help="CSV file to sort (use '-' for stdin).")
    p.add_argument(
        "-k", "--key",
        required=True,
        dest="keys",
        action="append",
        metavar="COLUMN",
        help="Column to sort by (repeatable; applied left-to-right).",
    )
    p.add_argument(
        "-d", "--direction",
        choices=["asc", "desc"],
        default="asc",
        help="Sort direction (default: asc).",
    )
    p.add_argument(
        "-o", "--output",
        default="-",
        metavar="FILE",
        help="Output file (default: stdout).",
    )
    p.set_defaults(func=cmd_sort)


def build_sort_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff-sort")
    sub = parser.add_subparsers(dest="command")
    _add_sort_parser(sub)
    return parser


def cmd_sort(args: argparse.Namespace) -> int:
    """Entry point for the 'sort' sub-command."""
    try:
        src = sys.stdin if args.file == "-" else open(args.file, newline="")  # noqa: WPS515
        rows: List[dict] = list(csv.DictReader(src))
        if args.file != "-":
            src.close()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not rows:
        return 0

    # Apply sort keys in *reverse* order so the first key is the primary sort.
    sorted_rows = rows
    for col in reversed(args.keys):
        try:
            sorted_rows = sort_rows(sorted_rows, col, direction=args.direction)
        except SortError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

    out = sys.stdout if args.output == "-" else open(args.output, "w", newline="")  # noqa: WPS515
    writer = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(sorted_rows)
    if args.output != "-":
        out.close()

    return 0
