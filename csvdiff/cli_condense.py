"""CLI sub-command: condense — group rows and join a column's values."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from csvdiff.condenser import CondenserError, condense


def _read_csv(path: str) -> tuple[List[str], List[dict]]:
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
            headers = list(reader.fieldnames or [])
        if rows:
            headers = list(rows[0].keys())
        return headers, rows
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)


def _write_csv(headers: List[str], rows: List[dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def cmd_condense(args: argparse.Namespace) -> int:
    _headers, rows = _read_csv(args.input)
    try:
        result = condense(
            rows,
            key_columns=args.key,
            agg_column=args.agg_column,
            separator=args.separator,
        )
    except CondenserError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.output:
        _write_csv(result.headers, result.rows, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=result.headers)
        writer.writeheader()
        writer.writerows(result.rows)

    if not args.quiet:
        print(
            f"condensed {result.original_count} rows "
            f"→ {result.condensed_count} rows "
            f"(removed {result.reduction_count}, "
            f"rate {result.reduction_rate:.1%})",
            file=sys.stderr,
        )
    return 0


def _add_condense_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "condense",
        help="Group rows by key columns and join an aggregated column's values.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("-k", "--key", nargs="+", required=True, metavar="COL",
                   help="Key column(s) to group by")
    p.add_argument("-a", "--agg-column", required=True, metavar="COL",
                   help="Column whose values will be joined")
    p.add_argument("-s", "--separator", default="|",
                   help="Separator string (default: '|')")
    p.add_argument("-o", "--output", default="",
                   help="Output CSV file (default: stdout)")
    p.add_argument("-q", "--quiet", action="store_true",
                   help="Suppress summary output")
    p.set_defaults(func=cmd_condense)


def build_condense_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csvdiff condense",
        description="Group CSV rows and join aggregated column values.",
    )
    subs = parser.add_subparsers()
    _add_condense_parser(subs)
    return parser
