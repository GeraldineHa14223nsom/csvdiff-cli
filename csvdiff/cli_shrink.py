"""CLI sub-command: shrink — truncate a column to a maximum character width."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Dict

from csvdiff.shrinker import shrink, ShrinkerError


def _read_csv(path: str) -> tuple[List[str], List[Dict[str, str]]]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        headers = list(reader.fieldnames or [])
    return headers, rows


def _write_csv(headers: List[str], rows: List[Dict[str, str]], fh) -> None:
    writer = csv.DictWriter(fh, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)


def cmd_shrink(args: argparse.Namespace) -> int:
    try:
        _, rows = _read_csv(args.file)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        result = shrink(
            rows,
            column=args.column,
            max_length=args.max_length,
            ellipsis_str=args.ellipsis,
        )
    except ShrinkerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            _write_csv(result.headers, result.rows, fh)
    else:
        _write_csv(result.headers, result.rows, sys.stdout)

    if args.stats:
        print(
            f"truncated {result.truncated_count}/{result.row_count} rows "
            f"({result.truncation_rate:.1%})",
            file=sys.stderr,
        )

    return 0


def _add_shrink_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("shrink", help="Truncate a column to a maximum character width")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("column", help="Column to truncate")
    p.add_argument("max_length", type=int, help="Maximum character length")
    p.add_argument("--ellipsis", default="...", help="Suffix appended to truncated values (default: '...')")
    p.add_argument("-o", "--output", default="", help="Output file (default: stdout)")
    p.add_argument("--stats", action="store_true", help="Print truncation statistics to stderr")
    p.set_defaults(func=cmd_shrink)


def build_shrink_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff-shrink")
    sub = parser.add_subparsers(dest="command")
    _add_shrink_parser(sub)
    return parser
