"""CLI sub-command: export diff result as TSV."""
from __future__ import annotations

import argparse
import sys

from csvdiff.core import diff
from csvdiff.formatter_tsv import TsvOptions, format_tsv


def _add_tsv_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "tsv",
        help="Export diff output as tab-separated values (TSV)",
    )
    p.add_argument("left", help="Left (baseline) CSV file")
    p.add_argument("right", help="Right (comparison) CSV file")
    p.add_argument(
        "--keys",
        nargs="+",
        default=["id"],
        metavar="COL",
        help="Key column(s) used to match rows (default: id)",
    )
    p.add_argument(
        "--output", "-o",
        default="-",
        metavar="FILE",
        help="Output file path (default: stdout)",
    )
    p.add_argument(
        "--title",
        default="CSV Diff Report",
        help="Report title written as a comment header",
    )
    p.add_argument(
        "--max-cell-width",
        type=int,
        default=60,
        dest="max_cell_width",
        help="Maximum cell width before truncation (default: 60)",
    )
    p.add_argument(
        "--no-section-headers",
        action="store_true",
        dest="no_section_headers",
        help="Omit section comment lines from output",
    )
    p.set_defaults(func=cmd_tsv)


def build_tsv_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff-tsv")
    subs = parser.add_subparsers()
    _add_tsv_parser(subs)
    return parser


def cmd_tsv(args: argparse.Namespace) -> int:
    try:
        result = diff(args.left, args.right, keys=args.keys)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    opts = TsvOptions(
        title=args.title,
        max_cell_width=args.max_cell_width,
        include_section_headers=not args.no_section_headers,
    )
    output = format_tsv(result, opts)

    if args.output == "-":
        sys.stdout.write(output)
    else:
        with open(args.output, "w", newline="") as fh:
            fh.write(output)

    return 0
