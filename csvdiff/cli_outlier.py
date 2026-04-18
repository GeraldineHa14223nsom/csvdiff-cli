"""CLI command for outlier detection."""
from __future__ import annotations
import argparse
import csv
import json
import sys
from csvdiff.outlier import detect_outliers, OutlierError


def _read_csv(path: str):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _render_text(result) -> str:
    lines = [
        f"Column   : {result.column}",
        f"Method   : {result.method}",
        f"Threshold: {result.threshold}",
        f"Total    : {result.total_rows()}",
        f"Outliers : {result.outlier_count()}",
    ]
    if result.outlier_rows:
        lines.append("\nOutlier rows:")
        for r in result.outlier_rows:
            lines.append("  " + ", ".join(f"{k}={v}" for k, v in r.items()))
    return "\n".join(lines)


def cmd_outlier(args: argparse.Namespace) -> int:
    try:
        rows = _read_csv(args.file)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        result = detect_outliers(
            rows,
            column=args.column,
            method=args.method,
            threshold=args.threshold,
        )
    except OutlierError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps({
            "column": result.column,
            "method": result.method,
            "threshold": result.threshold,
            "total_rows": result.total_rows(),
            "outlier_count": result.outlier_count(),
            "outlier_rows": result.outlier_rows,
        }))
    else:
        print(_render_text(result))
    return 0


def _add_outlier_parser(subparsers):
    p = subparsers.add_parser("outlier", help="Detect outliers in a numeric column")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("column", help="Numeric column to analyse")
    p.add_argument("--method", choices=["zscore", "iqr"], default="zscore")
    p.add_argument("--threshold", type=float, default=3.0)
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=cmd_outlier)
    return p


def build_outlier_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csvdiff-outlier")
    subs = parser.add_subparsers()
    _add_outlier_parser(subs)
    return parser
