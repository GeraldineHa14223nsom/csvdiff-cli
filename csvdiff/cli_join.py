"""CLI sub-command: join two CSV files on a key column."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from csvdiff.joiner import JoinError, join


def _read_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[dict], stream) -> None:
    if not rows:
        return
    writer = csv.DictWriter(stream, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def cmd_join(args: argparse.Namespace) -> int:
    try:
        left = _read_csv(args.left)
        right = _read_csv(args.right)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        result = join(left, right, key=args.key, how=args.how)
    except JoinError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output = result.rows
    if args.include_left_only:
        output = output + result.left_only
    if args.include_right_only:
        output = output + result.right_only

    out = open(args.output, "w", newline="", encoding="utf-8") if args.output else sys.stdout
    try:
        _write_csv(output, out)
    finally:
        if args.output:
            out.close()
    return 0


def _add_join_parser(sub: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = sub.add_parser("join", help="Join two CSV files on a key column")
    p.add_argument("left", help="Left CSV file")
    p.add_argument("right", help="Right CSV file")
    p.add_argument("--key", required=True, help="Column to join on")
    p.add_argument(
        "--how",
        choices=["inner", "left", "right", "outer"],
        default="inner",
        help="Join type (default: inner)",
    )
    p.add_argument("--output", "-o", default=None, help="Output file (default: stdout)")
    p.add_argument("--include-left-only", action="store_true", help="Append unmatched left rows")
    p.add_argument("--include-right-only", action="store_true", help="Append unmatched right rows")
    p.set_defaults(func=cmd_join)


def build_join_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff-join")
    sub = parser.add_subparsers(dest="command")
    _add_join_parser(sub)
    return parser
