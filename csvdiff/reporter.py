"""Human-readable summary reporting for diff results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TextIO
import sys

from csvdiff.core import DiffResult
from csvdiff.stats import DiffStats, as_dict


@dataclass
class ReportOptions:
    show_sample: bool = True
    sample_size: int = 3
    color: bool = True


_RESET = "\033[0m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BOLD = "\033[1m"


def _color(text: str, code: str, enabled: bool) -> str:
    return f"{code}{text}{_RESET}" if enabled else text


def _section(title: str, rows: list[dict], color: str, opts: ReportOptions) -> list[str]:
    lines: list[str] = []
    if not rows:
        return lines
    lines.append(_color(f"  {title}: {len(rows)}", color, opts.color))
    if opts.show_sample:
        for row in rows[: opts.sample_size]:
            lines.append(f"    {row}")
        if len(rows) > opts.sample_size:
            lines.append(f"    ... and {len(rows) - opts.sample_size} more")
    return lines


def build_report(result: DiffResult, opts: ReportOptions | None = None) -> str:
    """Return a formatted multi-line report string for *result*."""
    if opts is None:
        opts = ReportOptions()

    stats = as_dict(DiffStats.from_result(result))
    lines: list[str] = [
        _color("=== CSV Diff Report ===", _BOLD, opts.color),
        fAdded rows    : {stats['added']}",
        f"  Removed rows  : {stats['removed']}",
        f"  Modified rows : {stats['modified']}",
        f {stats['unchanged']}",
        f"  Change rate   : {stats['change_rate_pct']:.1f}%",
    ]

    lines += _section("Sample added", result.added, _GREEN, opts)
    lines += _section("Sample removed", result.removed, _RED, opts)
    lines += _section("Sample modified (new values)", result.modified, _YELLOW, opts)

    return "\n".join(lines)


def print_report(
    result: DiffResult,
    opts: ReportOptions | None = None,
    file: TextIO | None = None,
) -> None:
    """Print the report to *file* (defaults to stdout)."""
    print(build_report(result, opts), file=file or sys.stdout)
