"""Command-line interface for csvdiff-cli."""

import sys
import argparse
from pathlib import Path

from csvdiff.core import diff_files, has_differences, summary
from csvdiff.formatters import render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csvdiff",
        description="Diff two CSV files by configurable key columns.",
    )
    parser.add_argument("old", metavar="OLD", help="Path to the original CSV file.")
    parser.add_argument("new", metavar="NEW", help="Path to the new CSV file.")
    parser.add_argument(
        "-k",
        "--keys",
        metavar="COL",
        nargs="+",
        required=True,
        help="One or more column names that form the row key.",
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="fmt",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary line after the diff.",
    )
    parser.add_argument(
        "--ignore-columns",
        metavar="COL",
        nargs="+",
        default=None,
        help="Columns to exclude from comparison.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    old_path = Path(args.old)
    new_path = Path(args.new)

    for p in (old_path, new_path):
        if not p.exists():
            print(f"csvdiff: error: file not found: {p}", file=sys.stderr)
            return 2

    try:
        result = diff_files(
            old_path,
            new_path,
            keys=args.keys,
            ignore_columns=args.ignore_columns or [],
        )
    except (KeyError, ValueError) as exc:
        print(f"csvdiff: error: {exc}", file=sys.stderr)
        return 2

    output = render(result, fmt=args.fmt)
    if output:
        print(output)

    if args.summary:
        print(summary(result), file=sys.stderr)

    return 1 if has_differences(result) else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
