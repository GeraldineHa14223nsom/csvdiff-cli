"""CLI command: unpivot a CSV file (melt wide to long)."""
from __future__ import annotations
import argparse
import csv
import sys
from typing import List

from csvdiff.unpivotter import unpivot, UnpivotError


def _read_csv(path: str):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    return rows


def _write_csv(result, fh=None):
    out = fh or sys.stdout
    writer = csv.DictWriter(out, fieldnames=result.headers, lineterminator="\n")
    writer.writeheader()
    writer.writerows(result.rows)


def cmd_unpivot(args: argparse.Namespace) -> int:
    try:
        rows = _read_csv(args.file)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    id_columns = [c.strip() for c in args.id_columns.split(",")]
    value_columns = [c.strip() for c in args.value_columns.split(",")]

    try:
        result = unpivot(
            rows,
            id_columns=id_columns,
            value_columns=value_columns,
            var_name=args.var_name,
            value_name=args.value_name,
        )
    except UnpivotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            _write_csv(result, fh)
    else:
        _write_csv(result)

    return 0


def _add_unpivot_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("unpivot", help="melt wide CSV to long format")
    p.add_argument("file", help="input CSV file")
    p.add_argument("--id-columns", required=True, metavar="COLS",
                   help="comma-separated columns to keep as identifiers")
    p.add_argument("--value-columns", required=True, metavar="COLS",
                   help="comma-separated columns to melt into rows")
    p.add_argument("--var-name", default="variable", help="name for the variable column")
    p.add_argument("--value-name", default="value", help="name for the value column")
    p.add_argument("-o", "--output", default=None, help="output file (default: stdout)")
    p.set_defaults(func=cmd_unpivot)


def build_unpivot_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="csvdiff unpivot")
    sub = p.add_subparsers()
    _add_unpivot_parser(sub)
    return p
