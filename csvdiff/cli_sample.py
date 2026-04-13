"""CLI sub-commands for row sampling."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from csvdiff.pipeline import run
from csvdiff.sampler import SamplerError, sample_fraction, sample_result


def _add_sample_parser(subparsers) -> None:
    p = subparsers.add_parser("sample", help="Sample rows from a CSV diff")
    p.add_argument("left", help="Left (old) CSV file")
    p.add_argument("right", help="Right (new) CSV file")
    p.add_argument("-k", "--key", nargs="+", default=["id"], metavar="COL",
                   help="Key column(s) (default: id)")
    p.add_argument("-n", "--count", type=int, default=None, metavar="N",
                   help="Max rows per category")
    p.add_argument("--frac", type=float, default=None, metavar="F",
                   help="Fraction of rows per category (overrides -n)")
    p.add_argument("--seed", type=int, default=None, help="Random seed")
    p.add_argument("--include-unchanged", action="store_true",
                   help="Also sample unchanged rows")
    p.add_argument("--format", choices=["json", "text"], default="text",
                   dest="fmt", help="Output format (default: text)")
    p.set_defaults(func=cmd_sample)


def build_sample_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff-sample")
    sub = parser.add_subparsers()
    _add_sample_parser(sub)
    return parser


def _render_text(label: str, rows: List[dict]) -> None:
    if not rows:
        return
    print(f"=== {label} ({len(rows)}) ===")
    for row in rows:
        print("  " + ", ".join(f"{k}={v}" for k, v in row.items()))


def cmd_sample(args: argparse.Namespace) -> int:
    try:
        diff = run(args.left, args.right, key_cols=args.key)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        if args.frac is not None:
            sr = sample_fraction(diff, frac=args.frac, seed=args.seed)
        else:
            n = args.count if args.count is not None else 10
            sr = sample_result(
                diff, n=n, seed=args.seed,
                include_unchanged=args.include_unchanged,
            )
    except SamplerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.fmt == "json":
        out = {
            "added": sr.added,
            "removed": sr.removed,
            "modified": sr.modified,
        }
        if args.include_unchanged:
            out["unchanged"] = sr.unchanged
        print(json.dumps(out, indent=2))
    else:
        _render_text("added", sr.added)
        _render_text("removed", sr.removed)
        _render_text("modified", sr.modified)
        if args.include_unchanged:
            _render_text("unchanged", sr.unchanged)

    return 0
