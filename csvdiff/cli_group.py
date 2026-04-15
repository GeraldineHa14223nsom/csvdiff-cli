"""CLI sub-command: group — group CSV rows and optionally aggregate a column."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import List

from csvdiff.grouper import GrouperError, group_rows


def _read_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[dict], fh) -> None:
    if not rows:
        return
    writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def cmd_group(args: argparse.Namespace) -> int:
    try:
        rows = _read_csv(args.file)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    keys = [k.strip() for k in args.keys.split(",")]
    try:
        result = group_rows(rows, keys)
    except GrouperError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.agg_column and args.agg_func:
        try:
            summary_rows = result.to_summary_rows(args.agg_column, args.agg_func)
        except Exception as exc:  # noqa: BLE001
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if args.format == "json":
            print(json.dumps(summary_rows, indent=2))
        else:
            _write_csv(summary_rows, sys.stdout)
    else:
        if args.format == "json":
            info = {
                "group_keys": result.group_keys,
                "group_count": result.group_count(),
                "row_count": result.row_count(),
                "groups": {
                    "|".join(k): len(v) for k, v in result.groups.items()
                },
            }
            print(json.dumps(info, indent=2))
        else:
            print(f"group_keys : {', '.join(result.group_keys)}")
            print(f"group_count: {result.group_count()}")
            print(f"row_count  : {result.row_count()}")
            for k, v in result.groups.items():
                print(f"  {'|'.join(k)}: {len(v)} row(s)")

    return 0


def _add_group_parser(subparsers) -> None:
    p = subparsers.add_parser("group", help="Group rows by key columns")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("--keys", required=True, help="Comma-separated group key columns")
    p.add_argument("--agg-column", dest="agg_column", default="",
                   help="Column to aggregate within each group")
    p.add_argument("--agg-func", dest="agg_func", default="count",
                   choices=["count", "total", "min", "max", "mean"],
                   help="Aggregation function (default: count)")
    p.add_argument("--format", default="text", choices=["text", "json"],
                   help="Output format")
    p.set_defaults(func=cmd_group)


def build_group_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff-group")
    sub = parser.add_subparsers()
    _add_group_parser(sub)
    return parser
