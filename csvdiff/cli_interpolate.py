"""CLI entry-point for the interpolate sub-command."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from csvdiff.interpolator import interpolate, InterpolatorError


def _read_csv(path: str):
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
            headers = list(reader.fieldnames or [])
        return headers, rows
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)


def _write_csv(headers, rows, dest):
    writer = csv.DictWriter(dest, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)


def cmd_interpolate(args: argparse.Namespace) -> int:
    headers, rows = _read_csv(args.file)
    columns: List[str] = args.columns

    try:
        result = interpolate(rows, columns)
    except InterpolatorError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            _write_csv(result.headers or headers, result.rows, fh)
    else:
        _write_csv(result.headers or headers, result.rows, sys.stdout)

    if not args.quiet:
        print(
            f"interpolated {result.filled_count} cell(s) across column(s): "
            f"{', '.join(result.columns)}",
            file=sys.stderr,
        )
    return 0


def _add_interpolate_parser(sub) -> argparse.ArgumentParser:
    p = sub.add_parser(
        "interpolate",
        help="fill empty numeric cells using linear interpolation",
    )
    p.add_argument("file", help="input CSV file")
    p.add_argument(
        "--columns",
        nargs="+",
        required=True,
        metavar="COL",
        help="column(s) to interpolate",
    )
    p.add_argument("-o", "--output", metavar="FILE", help="write result to FILE")
    p.add_argument("-q", "--quiet", action="store_true", help="suppress summary")
    p.set_defaults(func=cmd_interpolate)
    return p


def build_interpolate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff interpolate")
    sub = parser.add_subparsers()
    _add_interpolate_parser(sub)
    return parser
