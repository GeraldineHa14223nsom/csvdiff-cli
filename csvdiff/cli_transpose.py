"""CLI subcommand: transpose a CSV file."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from csvdiff.transposer import transpose, TransposerError


def _read_csv(path: str):
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            headers = list(reader.fieldnames or [])
            rows = [dict(r) for r in reader]
        return headers, rows
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)


def _write_csv(headers, rows, dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def cmd_transpose(args: argparse.Namespace) -> int:
    headers, rows = _read_csv(args.input)
    try:
        result = transpose(headers, rows)
    except TransposerError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.output and args.output != "-":
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            _write_csv(result.headers, result.rows, fh)
    else:
        _write_csv(result.headers, result.rows, sys.stdout)

    if args.verbose:
        print(
            f"Transposed {result.original_row_count} rows x "
            f"{result.original_col_count} columns -> "
            f"{result.original_col_count} rows x "
            f"{result.original_row_count + 1} columns",
            file=sys.stderr,
        )
    return 0


def _add_transpose_parser(subparsers) -> None:
    p = subparsers.add_parser("transpose", help="Transpose rows and columns of a CSV")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("-o", "--output", default="-", help="Output file (default: stdout)")
    p.add_argument("-v", "--verbose", action="store_true", help="Print summary to stderr")
    p.set_defaults(func=cmd_transpose)


def build_transpose_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff transpose")
    subs = parser.add_subparsers()
    _add_transpose_parser(subs)
    return parser
