"""CLI command: rank rows by a numeric column."""
from __future__ import annotations
import argparse
import csv
import io
import sys
from csvdiff.ranker import rank_rows, RankerError


def _read_csv(path: str):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    return rows


def _write_csv(rows, outfile):
    if not rows:
        return
    writer = csv.DictWriter(outfile, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def cmd_rank(args, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    try:
        rows = _read_csv(args.file)
    except FileNotFoundError as exc:
        stderr.write(f"Error: {exc}\n")
        return 2
    try:
        result = rank_rows(
            rows,
            args.column,
            ascending=not args.desc,
            rank_column=args.rank_column,
            method=args.method,
        )
    except RankerError as exc:
        stderr.write(f"Error: {exc}\n")
        return 1
    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            _write_csv(result.rows, fh)
    else:
        _write_csv(result.rows, stdout)
    return 0


def _add_rank_parser(subparsers):
    p = subparsers.add_parser("rank", help="Rank rows by a numeric column")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("column", help="Column to rank by")
    p.add_argument("--desc", action="store_true", help="Rank descending")
    p.add_argument("--rank-column", default="rank", dest="rank_column",
                   help="Name of the new rank column (default: rank)")
    p.add_argument("--method", choices=["dense", "standard"], default="dense",
                   help="Tie-breaking method (default: dense)")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    return p


def build_rank_parser():
    parser = argparse.ArgumentParser(prog="csvdiff-rank")
    subs = parser.add_subparsers(dest="command")
    _add_rank_parser(subs)
    return parser
