"""CLI sub-command: profile — show per-column statistics for a CSV file."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import List

from csvdiff.profiler import profile_rows, ProfileResult


def _read_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _render_text(result: ProfileResult) -> str:
    lines = []
    for col in result.columns:
        p = result.profiles[col]
        lines.append(
            f"{col}: count={p.count}, non_empty={p.non_empty}, "
            f"fill_rate={p.fill_rate:.1%}, unique={p.unique_values}, "
            f"min_len={p.min_length}, max_len={p.max_length}"
        )
    return "\n".join(lines)


def _render_json(result: ProfileResult) -> str:
    data = [
        {
            "column": p.name,
            "count": p.count,
            "non_empty": p.non_empty,
            "empty_count": p.empty_count,
            "fill_rate": round(p.fill_rate, 4),
            "unique_values": p.unique_values,
            "min_length": p.min_length,
            "max_length": p.max_length,
            "sample_values": p.sample_values,
        }
        for p in (result.profiles[c] for c in result.columns)
    ]
    return json.dumps(data, indent=2)


def cmd_profile(args: argparse.Namespace) -> int:
    try:
        rows = _read_csv(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        return 2

    result = profile_rows(rows, sample_size=args.sample_size)

    if args.format == "json":
        print(_render_json(result))
    else:
        print(_render_text(result))
    return 0


def _add_profile_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("profile", help="Show per-column statistics for a CSV file")
    p.add_argument("file", help="CSV file to profile")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--sample-size", type=int, default=5, dest="sample_size")
    p.set_defaults(func=cmd_profile)


def build_profile_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff profile")
    sub = parser.add_subparsers()
    _add_profile_parser(sub)
    return parser
