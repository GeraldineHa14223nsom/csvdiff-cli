"""CLI command for rolling window calculations."""
from __future__ import annotations
import argparse
import csv
import sys
from csvdiff.roller import rolling, RollerError


def _read_csv(path: str):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(rows, path: str | None) -> None:
    if not rows:
        return
    dest = open(path, "w", newline="", encoding="utf-8") if path else sys.stdout
    try:
        w = csv.DictWriter(dest, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    finally:
        if path:
            dest.close()


def cmd_roll(args: argparse.Namespace) -> int:
    try:
        rows = _read_csv(args.file)
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        return 2
    try:
        result = rolling(rows, args.column, args.window,
                         func=args.func, new_column=args.new_column)
    except RollerError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    _write_csv(result.rows, getattr(args, "output", None))
    return 0


def _add_roll_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("roll", help="Compute rolling window statistics on a column")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("--column", required=True, help="Numeric column to compute over")
    p.add_argument("--window", type=int, required=True, help="Window size")
    p.add_argument("--func", default="mean", choices=["mean", "sum", "min", "max"])
    p.add_argument("--new-column", dest="new_column", default=None)
    p.add_argument("--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(cmd=cmd_roll)


def build_roll_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    s = p.add_subparsers()
    _add_roll_parser(s)
    return p
