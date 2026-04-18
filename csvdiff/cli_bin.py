"""CLI sub-command: bin — assign numeric values to labelled buckets."""
from __future__ import annotations
import argparse
import csv
import json
import sys
from csvdiff.binner import bin_column, BinnerError


def _read_csv(path: str):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    return rows


def _write_csv(rows, headers, dest):
    writer = csv.DictWriter(dest, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)


def cmd_bin(args: argparse.Namespace) -> int:
    try:
        rows = _read_csv(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 2
    boundaries = list(map(float, args.boundaries))
    labels = args.labels if args.labels else None
    try:
        result = bin_column(
            rows,
            column=args.column,
            boundaries=boundaries,
            labels=labels,
            bin_column=args.bin_column or "",
            out_of_range=args.out_of_range,
        )
    except BinnerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(result.rows, indent=2))
    elif args.format == "stats":
        for label, count in result.bin_counts.items():
            print(f"{label}: {count}")
    else:
        _write_csv(result.rows, result.headers, sys.stdout)
    return 0


def _add_bin_parser(subparsers) -> None:
    p = subparsers.add_parser("bin", help="Bin a numeric column into labelled buckets.")
    p.add_argument("file", help="Input CSV file.")
    p.add_argument("--column", required=True, help="Numeric column to bin.")
    p.add_argument(
        "--boundaries", nargs="+", required=True, metavar="N",
        help="Ordered boundary values (at least two)."
    )
    p.add_argument("--labels", nargs="+", default=[], help="Optional bin labels.")
    p.add_argument("--bin-column", default="", help="Name for the new bin column.")
    p.add_argument("--out-of-range", default="other", help="Label for out-of-range values.")
    p.add_argument(
        "--format", choices=["csv", "json", "stats"], default="csv",
        help="Output format."
    )
    p.set_defaults(func=cmd_bin)


def build_bin_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff-bin")
    sub = parser.add_subparsers()
    _add_bin_parser(sub)
    return parser
