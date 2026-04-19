"""CLI command for window/lag operations."""
from __future__ import annotations
import argparse
import csv
import sys
from csvdiff.windower import window_lag, WindowError


def _read_csv(path: str):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    return rows


def _write_csv(rows, path: str) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def cmd_window(args: argparse.Namespace) -> int:
    try:
        rows = _read_csv(args.file)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        result = window_lag(
            rows,
            column=args.column,
            lag=args.lag,
            new_column=args.new_column or None,
            fill=args.fill,
        )
    except WindowError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _write_csv(result.rows, args.output)
    return 0


def _add_window_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("window", help="Add lag column to a CSV file.")
    p.add_argument("file", help="Input CSV file.")
    p.add_argument("--column", required=True, help="Source column for lag.")
    p.add_argument("--lag", type=int, default=1, help="Number of rows to lag (default 1).")
    p.add_argument("--new-column", default="", help="Name for the new lag column.")
    p.add_argument("--fill", default="", help="Fill value for rows without a lag value.")
    p.add_argument("--output", required=True, help="Output CSV file.")
    p.set_defaults(func=cmd_window)


def build_window_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff-window")
    sub = parser.add_subparsers(dest="command")
    _add_window_parser(sub)
    return parser
