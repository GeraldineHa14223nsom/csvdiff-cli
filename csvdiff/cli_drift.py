"""CLI command for detecting schema drift between two CSV files."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import List

from csvdiff.drifter import DrifterError, detect_drift


def _read_headers(path: str) -> List[str]:
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            headers = next(reader, [])
        if not headers:
            raise DrifterError(f"File '{path}' has no headers.")
        return headers
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)


def cmd_drift(args: argparse.Namespace) -> int:
    left_headers = _read_headers(args.left)
    right_headers = _read_headers(args.right)

    try:
        result = detect_drift(left_headers, right_headers)
    except DrifterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        payload = {
            "has_drift": result.has_drift,
            "added": result.added,
            "removed": result.removed,
            "reordered": result.reordered,
            "left_column_count": result.column_count_left,
            "right_column_count": result.column_count_right,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"Schema drift detected: {result.has_drift}")
        print(f"  Columns added   : {result.added or '—'}")
        print(f"  Columns removed : {result.removed or '—'}")
        print(f"  Reordered       : {result.reordered}")
        print(f"  Left columns    : {result.column_count_left}")
        print(f"  Right columns   : {result.column_count_right}")

    return 1 if result.has_drift else 0


def _add_drift_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("drift", help="Detect schema drift between two CSV files")
    p.add_argument("left", help="Path to the left (baseline) CSV file")
    p.add_argument("right", help="Path to the right (comparison) CSV file")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.set_defaults(func=cmd_drift)


def build_drift_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect schema drift between CSV files")
    sub = parser.add_subparsers(dest="command")
    _add_drift_parser(sub)
    return parser
