"""CLI command: export diff result as Excel-compatible CSV."""
from __future__ import annotations

import argparse
import sys

from csvdiff.core import _read_csv, diff
from csvdiff.formatter_excel import ExcelOptions, format_excel_csv


def _add_excel_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "excel",
        help="Export diff as Excel-compatible multi-section CSV",
    )
    p.add_argument("left", help="Left (baseline) CSV file")
    p.add_argument("right", help="Right (revised) CSV file")
    p.add_argument(
        "--keys",
        nargs="+",
        default=["id"],
        metavar="COL",
        help="Key column(s) used to match rows (default: id)",
    )
    p.add_argument(
        "--max-col-width",
        type=int,
        default=64,
        metavar="N",
        help="Truncate cell values to N characters (default: 64)",
    )
    p.add_argument(
        "--include-unchanged",
        action="store_true",
        help="Include unchanged rows in output",
    )
    p.add_argument(
        "--output", "-o",
        default="-",
        metavar="FILE",
        help="Output file path (default: stdout)",
    )
    p.set_defaults(func=cmd_excel)


def build_excel_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="csvdiff excel")
    subs = p.add_subparsers()
    _add_excel_parser(subs)
    return p


def cmd_excel(args: argparse.Namespace) -> int:
    try:
        left_rows = _read_csv(args.left)
        right_rows = _read_csv(args.right)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = diff(left_rows, right_rows, keys=args.keys)
    opts = ExcelOptions(
        max_col_width=args.max_col_width,
        include_unchanged=args.include_unchanged,
    )
    output = format_excel_csv(result, opts)

    if args.output == "-":
        sys.stdout.write(output)
    else:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            fh.write(output)

    return 0
