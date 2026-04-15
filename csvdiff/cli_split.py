"""CLI sub-commands for splitting CSV files."""
from __future__ import annotations

import argparse
import csv
import pathlib
import sys
from typing import List

from csvdiff.splitter import SplitterError, chunk_to_csv, split_by_column, split_by_count


def _read_csv(path: str) -> List[dict]:
    """Read a CSV file and return its rows as a list of dicts."""
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_chunks(result, out_dir: pathlib.Path) -> None:
    """Write each chunk in *result* to a separate CSV file under *out_dir*."""
    for key, chunk_rows in result.chunks.items():
        safe_key = key.replace("/", "_").replace("\\", "_")
        dest = out_dir / f"chunk_{safe_key}.csv"
        dest.write_text(chunk_to_csv(chunk_rows), encoding="utf-8")
        print(f"wrote {len(chunk_rows)} rows -> {dest}")


def cmd_split(args: argparse.Namespace) -> int:
    """Entry point for the *split* sub-command."""
    try:
        rows = _read_csv(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2

    if not rows:
        print("error: input file is empty or has no data rows", file=sys.stderr)
        return 1

    try:
        if args.by_column:
            result = split_by_column(rows, args.by_column)
        else:
            result = split_by_count(rows, args.chunk_size)
    except SplitterError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    out_dir = pathlib.Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_chunks(result, out_dir)

    print(f"total chunks: {result.chunk_count}, total rows: {result.total_rows}")
    return 0


def _add_split_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("split", help="Split a CSV file into multiple chunks")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("-o", "--output-dir", default=".", help="Directory for output chunks")
    group = p.add_mutually_exclusive_group()
    group.add_argument("-n", "--chunk-size", type=int, default=1000,
                       help="Maximum rows per chunk (default: 1000)")
    group.add_argument("-c", "--by-column", metavar="COLUMN",
                       help="Split by distinct values of COLUMN")
    p.set_defaults(func=cmd_split)


def build_split_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff split")
    sub = parser.add_subparsers()
    _add_split_parser(sub)
    return parser
