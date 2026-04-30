"""CLI subcommand: export diff as LaTeX tabular output."""
from __future__ import annotations

import argparse
import sys

from csvdiff.core import _read_csv, diff
from csvdiff.formatter_latex import LatexOptions, format_latex


def _add_latex_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "latex",
        help="Export diff result as LaTeX tabular format",
    )
    p.add_argument("left", help="Left (base) CSV file")
    p.add_argument("right", help="Right (new) CSV file")
    p.add_argument(
        "--keys",
        nargs="+",
        default=[],
        metavar="COL",
        help="Key columns for matching rows",
    )
    p.add_argument("--title", default="CSV Diff Report", help="Report title")
    p.add_argument(
        "--max-col-width",
        type=int,
        default=40,
        dest="max_col_width",
        help="Maximum column width before truncation",
    )
    p.add_argument(
        "--show-unchanged",
        action="store_true",
        default=False,
        dest="show_unchanged",
        help="Include unchanged rows in output",
    )
    p.add_argument(
        "--output", "-o",
        default="-",
        help="Output file path (default: stdout)",
    )
    p.set_defaults(func=cmd_latex)


def build_latex_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="csvdiff-latex")
    sub = p.add_subparsers()
    _add_latex_parser(sub)
    return p


def cmd_latex(args: argparse.Namespace) -> int:
    try:
        left_rows = _read_csv(args.left)
        right_rows = _read_csv(args.right)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = diff(left_rows, right_rows, keys=args.keys)
    opts = LatexOptions(
        title=args.title,
        max_col_width=args.max_col_width,
        show_unchanged=args.show_unchanged,
    )
    output = format_latex(result, opts)

    if args.output == "-":
        print(output)
    else:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
            fh.write("\n")

    return 0
