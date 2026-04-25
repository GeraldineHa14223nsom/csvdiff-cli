"""CLI interface for the sequencer module."""
from __future__ import annotations

import csv
import sys
from argparse import ArgumentParser, Namespace
from typing import List, Dict

from csvdiff.sequencer import SequencerError, sequence_rows


def _read_csv(path: str) -> List[Dict[str, str]]:
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)


def _write_csv(rows: List[Dict[str, str]], path: str | None) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    dest = open(path, "w", newline="", encoding="utf-8") if path else sys.stdout
    try:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if path:
            dest.close()


def cmd_sequence(args: Namespace) -> int:
    rows = _read_csv(args.file)
    try:
        result = sequence_rows(
            rows,
            column=args.column,
            start=args.start,
            step=args.step,
            overwrite=args.overwrite,
        )
    except SequencerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _write_csv(result.rows, args.output)
    return 0


def _add_sequence_parser(sub) -> None:
    p = sub.add_parser("sequence", help="add a sequential number column to a CSV file")
    p.add_argument("file", help="input CSV file")
    p.add_argument("--column", default="seq", help="name of the new sequence column (default: seq)")
    p.add_argument("--start", type=int, default=1, help="starting value (default: 1)")
    p.add_argument("--step", type=int, default=1, help="step between values (default: 1)")
    p.add_argument("--overwrite", action="store_true", help="allow overwriting an existing column")
    p.add_argument("--output", "-o", default=None, help="output file (default: stdout)")
    p.set_defaults(func=cmd_sequence)


def build_sequence_parser() -> ArgumentParser:
    parser = ArgumentParser(description="Add sequential row numbers to a CSV file.")
    sub = parser.add_subparsers()
    _add_sequence_parser(sub)
    return parser
