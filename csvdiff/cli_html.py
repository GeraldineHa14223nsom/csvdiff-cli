"""CLI sub-command: export diff as an HTML report."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from csvdiff.core import diff
from csvdiff.formatter_html import HtmlOptions, format_html


def _add_html_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "html",
        help="Render diff as an HTML report",
    )
    p.add_argument("left", help="Original CSV file")
    p.add_argument("right", help="New CSV file")
    p.add_argument(
        "--keys",
        nargs="+",
        default=[],
        metavar="COL",
        help="Key column(s) for matching rows",
    )
    p.add_argument("--title", default="CSV Diff Report", help="HTML page title")
    p.add_argument(
        "--max-rows",
        type=int,
        default=200,
        dest="max_rows",
        help="Maximum rows per section (default: 200)",
    )
    p.add_argument(
        "--show-unchanged",
        action="store_true",
        dest="show_unchanged",
        help="Include unchanged rows in the report",
    )
    p.add_argument("-o", "--output", default="-", help="Output file (default: stdout)")
    p.set_defaults(func=cmd_html)


def build_html_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff-html")
    sub = parser.add_subparsers()
    _add_html_parser(sub)
    return parser


def cmd_html(args: argparse.Namespace) -> int:
    try:
        result = diff(args.left, args.right, key_columns=args.keys)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    opts = HtmlOptions(
        title=args.title,
        max_rows=args.max_rows,
        show_unchanged=args.show_unchanged,
    )
    html = format_html(result, opts)

    if args.output == "-":
        sys.stdout.write(html)
    else:
        Path(args.output).write_text(html, encoding="utf-8")

    return 0
