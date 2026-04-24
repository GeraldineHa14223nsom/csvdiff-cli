"""CLI entry point for the tag subcommand."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from csvdiff.tagger import TaggerError, tag_rows


def _read_csv(path: str) -> tuple:
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
            headers = list(reader.fieldnames or [])
        return headers, rows
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)


def _write_csv(headers: List[str], rows, dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=headers, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def cmd_tag(args: argparse.Namespace) -> int:
    _headers, rows = _read_csv(args.file)
    values = set(v.strip() for v in args.values.split(","))
    try:
        result = tag_rows(
            rows,
            column=args.column,
            values=values,
            tag_column=args.tag_column,
            match_label=args.match_label,
            no_match_label=args.no_match_label,
        )
    except TaggerError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            _write_csv(result.headers, result.rows, fh)
    else:
        _write_csv(result.headers, result.rows, sys.stdout)

    print(
        f"tagged={result.tagged_count} untagged={result.untagged_count}",
        file=sys.stderr,
    )
    return 0


def _add_tag_parser(subparsers) -> None:
    p = subparsers.add_parser("tag", help="Tag rows based on column value membership")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("--column", required=True, help="Column to test")
    p.add_argument("--values", required=True, help="Comma-separated set of values")
    p.add_argument("--tag-column", default="tag", help="Name of new tag column")
    p.add_argument("--match-label", default="match", help="Label for matching rows")
    p.add_argument("--no-match-label", default="", help="Label for non-matching rows")
    p.add_argument("--output", "-o", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=cmd_tag)


def build_tag_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff tag")
    subs = parser.add_subparsers()
    _add_tag_parser(subs)
    return parser
