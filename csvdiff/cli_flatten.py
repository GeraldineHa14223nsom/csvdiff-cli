"""CLI sub-command: flatten a JSON column in a CSV file."""
from __future__ import annotations

import argparse
import csv
import sys

from csvdiff.flattener import FlattenerError, flatten_column


def _read_csv(path: str) -> tuple[list[str], list[dict[str, str]]]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        headers = list(reader.fieldnames or [])
    return headers, rows


def _write_csv(headers: list[str], rows: list[dict[str, str]], dest: str | None) -> None:
    out = open(dest, "w", newline="", encoding="utf-8") if dest else sys.stdout
    try:
        writer = csv.DictWriter(out, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if dest:
            out.close()


def cmd_flatten(args: argparse.Namespace) -> int:
    try:
        _headers, rows = _read_csv(args.file)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        result = flatten_column(
            rows,
            column=args.column,
            prefix=args.prefix or "",
            drop_source=args.drop_source,
        )
    except FlattenerError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    _write_csv(result.headers, result.rows, args.output)
    if args.verbose:
        print(
            f"Flattened '{result.source_column}': {len(result.new_columns)} new column(s).",
            file=sys.stderr,
        )
    return 0


def _add_flatten_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("flatten", help="Flatten a JSON-valued column into separate columns")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("column", help="Column containing JSON objects")
    p.add_argument("--prefix", default="", help="Prefix for new column names")
    p.add_argument("--drop-source", action="store_true", help="Remove the source column")
    p.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    p.add_argument("-v", "--verbose", action="store_true", help="Print summary to stderr")
    p.set_defaults(func=cmd_flatten)


def build_flatten_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff-flatten")
    sub = parser.add_subparsers(dest="command")
    _add_flatten_parser(sub)
    return parser
