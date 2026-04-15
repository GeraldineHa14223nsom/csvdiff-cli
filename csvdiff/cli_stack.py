"""CLI sub-command: stack — vertically concatenate CSV files."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Dict

from csvdiff.stacker import stack, StackerError


def _read_csv(path: str):
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            headers = list(reader.fieldnames or [])
            rows = [dict(r) for r in reader]
        return headers, rows
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(2)


def _write_csv(headers: List[str], rows: List[Dict[str, str]], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def cmd_stack(args: argparse.Namespace) -> int:
    if len(args.files) < 2:
        print("Error: at least two CSV files are required.", file=sys.stderr)
        return 2

    datasets, headers_list = [], []
    for path in args.files:
        h, r = _read_csv(path)
        headers_list.append(h)
        datasets.append(r)

    try:
        result = stack(
            datasets,
            headers_list,
            strict=not args.no_strict,
            fill_value=args.fill_value,
        )
    except StackerError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.output:
        _write_csv(result.headers, result.rows, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=result.headers)
        writer.writeheader()
        writer.writerows(result.rows)

    if args.summary:
        print(
            f"Stacked {result.source_count} files, "
            f"{result.total_rows} total rows.",
            file=sys.stderr,
        )
    return 0


def _add_stack_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("stack", help="Vertically concatenate CSV files.")
    p.add_argument("files", nargs="+", metavar="FILE", help="CSV files to stack.")
    p.add_argument("-o", "--output", metavar="FILE", help="Write output to FILE.")
    p.add_argument(
        "--no-strict",
        action="store_true",
        help="Allow files with different columns (fills missing with fill-value).",
    )
    p.add_argument(
        "--fill-value",
        default="",
        metavar="VALUE",
        help="Value to use for missing columns in non-strict mode (default: empty).",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary line to stderr after stacking.",
    )
    p.set_defaults(func=cmd_stack)


def build_stack_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff stack")
    sub = parser.add_subparsers()
    _add_stack_parser(sub)
    return parser
