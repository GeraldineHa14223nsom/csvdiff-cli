"""CLI entry-point for the anonymize subcommand."""
from __future__ import annotations
import argparse
import csv
import sys
from typing import List

from csvdiff.anonymizer import anonymize, AnonymizerError


def _read_csv(path: str) -> tuple:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        headers = list(reader.fieldnames or [])
    return headers, rows


def _write_csv(rows, headers, fh) -> None:
    writer = csv.DictWriter(fh, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)


def cmd_anonymize(args: argparse.Namespace) -> int:
    try:
        headers, rows = _read_csv(args.file)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    columns: List[str] = args.columns
    try:
        result = anonymize(
            rows,
            columns,
            method=args.method,
            salt=args.salt or "",
            mask_char=args.mask_char,
            keep=args.keep,
        )
    except AnonymizerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _write_csv(result.rows, result.headers, sys.stdout)
    return 0


def _add_anonymize_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("anonymize", help="Anonymize columns by hashing or masking")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("--columns", nargs="+", required=True, metavar="COL", help="Columns to anonymize")
    p.add_argument("--method", choices=["hash", "mask"], default="hash", help="Anonymization method")
    p.add_argument("--salt", default="", help="Salt for hashing")
    p.add_argument("--mask-char", default="*", dest="mask_char", help="Mask character")
    p.add_argument("--keep", type=int, default=0, help="Characters to keep when masking")
    p.set_defaults(func=cmd_anonymize)


def build_anonymize_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="csvdiff anonymize")
    sub = p.add_subparsers()
    _add_anonymize_parser(sub)
    return p
