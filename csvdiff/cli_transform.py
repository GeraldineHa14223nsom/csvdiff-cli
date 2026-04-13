"""CLI sub-commands for column transforms and renames."""

from __future__ import annotations

import argparse
import csv
import sys
from typing import Dict, List

from csvdiff.transform import TransformError, apply_transforms, rename_columns


def _parse_mapping(pairs: List[str], flag: str) -> Dict[str, str]:
    """Parse a list of 'key=value' strings into a dict."""
    result: Dict[str, str] = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise argparse.ArgumentTypeError(
                f"--{flag} values must be in COL=VALUE format, got {pair!r}"
            )
        k, _, v = pair.partition("=")
        result[k.strip()] = v.strip()
    return result


def cmd_transform(args: argparse.Namespace) -> int:
    """Apply transforms and/or renames to a CSV file, writing to stdout."""
    try:
        transforms: Dict[str, str] = _parse_mapping(args.transform, "transform")
        renames: Dict[str, str] = _parse_mapping(args.rename, "rename")
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        reader = csv.DictReader(args.input)
        rows = list(reader)
    except Exception as exc:  # noqa: BLE001
        print(f"error reading input: {exc}", file=sys.stderr)
        return 2

    try:
        if transforms:
            rows = apply_transforms(rows, transforms)
        if renames:
            rows = rename_columns(rows, renames)
    except TransformError as exc:
        print(f"transform error: {exc}", file=sys.stderr)
        return 1

    if not rows:
        return 0

    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(args.output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return 0


def _add_transform_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser(
        "transform",
        help="Apply column transforms and/or renames to a CSV file.",
    )
    p.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        metavar="FILE",
        help="Input CSV file (default: stdin).",
    )
    p.add_argument(
        "--transform",
        nargs="+",
        metavar="COL=TRANSFORM",
        help="Apply a named transform to a column, e.g. name=upper.",
    )
    p.add_argument(
        "--rename",
        nargs="+",
        metavar="OLD=NEW",
        help="Rename a column, e.g. full_name=name.",
    )
    p.add_argument(
        "--output",
        "-o",
        type=argparse.FileType("w"),
        default=sys.stdout,
        metavar="FILE",
        help="Output file (default: stdout).",
    )
    p.set_defaults(func=cmd_transform)


def build_transform_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csvdiff-transform",
        description="Transform CSV columns.",
    )
    sub = parser.add_subparsers(dest="command")
    _add_transform_parser(sub)
    return parser
