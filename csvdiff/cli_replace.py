"""CLI sub-command: replace — find-and-replace values in a CSV column."""
from __future__ import annotations

import csv
import sys
from argparse import ArgumentParser, Namespace
from typing import List

from csvdiff.replacer import ReplacerError, replace_values


def _read_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[dict], headers: List[str]) -> None:
    writer = csv.DictWriter(sys.stdout, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)


def cmd_replace(args: Namespace) -> int:
    try:
        rows = _read_csv(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2

    try:
        result = replace_values(
            rows,
            column=args.column,
            pattern=args.pattern,
            replacement=args.replacement,
            regex=args.regex,
            case_sensitive=not args.ignore_case,
        )
    except ReplacerError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    _write_csv(result.rows, result.headers)

    if args.verbose:
        print(
            f"Replaced {result.replaced_count} of {result.row_count} rows "
            f"in column '{result.column}'.",
            file=sys.stderr,
        )
    return 0


def _add_replace_parser(sub) -> None:
    p: ArgumentParser = sub.add_parser(
        "replace",
        help="Find-and-replace values in a CSV column.",
    )
    p.add_argument("file", help="Input CSV file")
    p.add_argument("column", help="Column to apply replacement in")
    p.add_argument("pattern", help="Pattern to search for")
    p.add_argument("replacement", help="Replacement value")
    p.add_argument(
        "--regex", action="store_true", default=False,
        help="Treat pattern as a regular expression",
    )
    p.add_argument(
        "--ignore-case", action="store_true", default=False,
        help="Case-insensitive matching",
    )
    p.add_argument(
        "--verbose", "-v", action="store_true", default=False,
        help="Print replacement summary to stderr",
    )
    p.set_defaults(func=cmd_replace)


def build_replace_parser() -> ArgumentParser:
    parser = ArgumentParser(prog="csvdiff replace")
    sub = parser.add_subparsers()
    _add_replace_parser(sub)
    return parser
