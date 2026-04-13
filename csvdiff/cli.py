"""Command-line interface for csvdiff."""
from __future__ import annotations

import sys
import argparse
from pathlib import Path

from csvdiff.core import diff_csv, has_differences
from csvdiff.formatters import render
from csvdiff.reconcile import reconcile_to_csv


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="csvdiff",
        description="Diff and reconcile CSV files.",
    )
    p.add_argument("old", help="Original CSV file")
    p.add_argument("new", help="New CSV file")
    p.add_argument(
        "-k", "--key",
        required=True,
        help="Comma-separated list of key column names",
    )
    p.add_argument(
        "-f", "--format",
        choices=["text", "json", "csv"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--reconcile",
        metavar="OUTPUT",
        help="Write reconciled CSV (old + changes) to OUTPUT file",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colour in text output",
    )
    return p


def main(argv: list[str] | None = None) -> int:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args(argv)

    for path in (args.old, args.new):
        if not Path(path).exists():
            print(f"csvdiff: file not found: {path}", file=sys.stderr)
            return 2

    key_cols = [k.strip() for k in args.key.split(",")]

    try:
        result = diff_csv(args.old, args.new, key_cols)
    except Exception as exc:  # noqa: BLE001
        print(f"csvdiff: error reading files: {exc}", file=sys.stderr)
        return 2

    print(render(result, fmt=args.fmt))

    if args.reconcile:
        from csvdiff.core import _read_csv  # local import to keep top-level clean
        base_rows = _read_csv(args.old)
        csv_out = reconcile_to_csv(result, base_rows, key_cols)
        Path(args.reconcile).write_text(csv_out, encoding="utf-8")
        print(f"Reconciled output written to {args.reconcile}", file=sys.stderr)

    return 1 if has_differences(result) else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
