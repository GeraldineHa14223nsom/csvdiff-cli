"""CLI sub-command: scale a numeric column."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from csvdiff.scaler import scale, ScalerError


def _read_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[dict], dest) -> None:
    if not rows:
        return
    writer = csv.DictWriter(dest, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def cmd_scale(args: argparse.Namespace) -> int:
    try:
        rows = _read_csv(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2

    try:
        result = scale(rows, column=args.column, method=args.method)
    except ScalerError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            _write_csv(result.rows, fh)
    else:
        _write_csv(result.rows, sys.stdout)

    if args.stats:
        print(
            f"# scaled {result.scaled_count} rows | method={result.method} "
            f"| original range=[{result.original_min}, {result.original_max}]",
            file=sys.stderr,
        )
    return 0


def _add_scale_parser(subparsers) -> None:
    p = subparsers.add_parser("scale", help="Scale a numeric column (minmax or zscore)")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("column", help="Column to scale")
    p.add_argument(
        "--method",
        choices=["minmax", "zscore"],
        default="minmax",
        help="Scaling method (default: minmax)",
    )
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.add_argument("--stats", action="store_true", help="Print scaling stats to stderr")
    p.set_defaults(func=cmd_scale)


def build_scale_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff-scale")
    subs = parser.add_subparsers()
    _add_scale_parser(subs)
    return parser
