"""CLI sub-commands for patch generation and application."""

from __future__ import annotations

import csv
import sys
from argparse import ArgumentParser, Namespace

from csvdiff.core import _read_csv, diff  # type: ignore[attr-defined]
from csvdiff.patch import apply_patch, load_patch, write_patch


def _add_generate_parser(sub: Any) -> None:  # type: ignore[name-defined]
    p = sub.add_parser("generate", help="Generate a JSON patch from two CSV files")
    p.add_argument("old", help="Original CSV file")
    p.add_argument("new", help="Updated CSV file")
    p.add_argument("-k", "--key", required=True, nargs="+", metavar="COL", help="Key column(s)")
    p.add_argument("-o", "--output", default="-", help="Output file (default: stdout)")


def _add_apply_parser(sub: Any) -> None:  # type: ignore[name-defined]
    p = sub.add_parser("apply", help="Apply a JSON patch to a CSV file")
    p.add_argument("base", help="Base CSV file")
    p.add_argument("patch", help="JSON patch file produced by 'generate'")
    p.add_argument("-o", "--output", default="-", help="Output file (default: stdout)")


def build_patch_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="csvpatch",
        description="Generate or apply CSV diff patches.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    _add_generate_parser(sub)
    _add_apply_parser(sub)
    return parser


def _open_output(path: str):
    if path == "-":
        return sys.stdout
    return open(path, "w", newline="", encoding="utf-8")


def cmd_generate(args: Namespace) -> int:
    try:
        old_rows = _read_csv(args.old)
        new_rows = _read_csv(args.new)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = diff(old_rows, new_rows, keys=args.key)
    fp = _open_output(args.output)
    try:
        write_patch(result, keys=args.key, fp=fp)
    finally:
        if fp is not sys.stdout:
            fp.close()
    return 0


def cmd_apply(args: Namespace) -> int:
    try:
        base_rows = _read_csv(args.base)
        with open(args.patch, encoding="utf-8") as pf:
            patch = load_patch(pf)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    patched = apply_patch(base_rows, patch)
    fp = _open_output(args.output)
    try:
        if patched:
            writer = csv.DictWriter(fp, fieldnames=list(patched[0].keys()))
            writer.writeheader()
            writer.writerows(patched)
    finally:
        if fp is not sys.stdout:
            fp.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_patch_parser()
    args = parser.parse_args(argv)
    if args.command == "generate":
        return cmd_generate(args)
    if args.command == "apply":
        return cmd_apply(args)
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
