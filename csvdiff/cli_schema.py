"""CLI sub-command: validate — check that two CSV files are schema-compatible."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from csvdiff.schema import validate_columns


def _read_headers(path: str) -> List[str]:
    """Return the header row of a CSV file without loading the full file."""
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            headers = next(reader, [])
        return headers
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except StopIteration:
        return []


def cmd_validate(args: argparse.Namespace) -> int:
    """Entry point for the 'validate' sub-command.

    Returns an exit code: 0 = compatible, 1 = incompatible, 2 = error.
    """
    left_headers = _read_headers(args.left)
    right_headers = _read_headers(args.right)

    key_columns: List[str] = args.key
    strict: bool = args.strict

    result = validate_columns(left_headers, right_headers, key_columns, strict=strict)

    if result.valid:
        if not args.quiet:
            print("Schema OK: files are compatible.")
        return 0

    print("Schema validation FAILED:", file=sys.stderr)
    for error in result.errors:
        print(f"  {error}", file=sys.stderr)
    return 1


def _add_validate_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "validate",
        help="Check that two CSV files are schema-compatible before diffing.",
    )
    p.add_argument("left", help="Base CSV file.")
    p.add_argument("right", help="Comparison CSV file.")
    p.add_argument(
        "-k",
        "--key",
        nargs="+",
        default=[],
        metavar="COL",
        help="Key columns that must be present in both files.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Require both files to have identical column sets.",
    )
    p.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress output on success.",
    )
    p.set_defaults(func=cmd_validate)


def build_validate_parser() -> argparse.ArgumentParser:
    """Standalone parser for the validate command (useful for testing)."""
    parser = argparse.ArgumentParser(
        prog="csvdiff validate",
        description="Validate CSV schema compatibility.",
    )
    sub = parser.add_subparsers(dest="command")
    _add_validate_parser(sub)
    return parser
