"""Row sampling utilities for large CSV diffs."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.core import DiffResult


class SamplerError(Exception):
    """Raised when sampling configuration is invalid."""

    def __str__(self) -> str:  # pragma: no cover
        return f"SamplerError: {self.args[0]}"


@dataclass
class SampleResult:
    added: List[Dict] = field(default_factory=list)
    removed: List[Dict] = field(default_factory=list)
    modified: List[Dict] = field(default_factory=list)
    unchanged: List[Dict] = field(default_factory=list)


def _sample(rows: List[Dict], n: int, seed: Optional[int]) -> List[Dict]:
    """Return up to *n* rows, optionally with a fixed random seed."""
    if n <= 0:
        raise SamplerError(f"sample size must be a positive integer, got {n}")
    if len(rows) <= n:
        return list(rows)
    rng = random.Random(seed)
    return rng.sample(rows, n)


def sample_result(
    result: DiffResult,
    n: int = 10,
    seed: Optional[int] = None,
    include_unchanged: bool = False,
) -> SampleResult:
    """Sample up to *n* rows from each change category in *result*."""
    if n <= 0:
        raise SamplerError(f"sample size must be a positive integer, got {n}")
    sampled = SampleResult(
        added=_sample(result.added, n, seed),
        removed=_sample(result.removed, n, seed),
        modified=_sample(result.modified, n, seed),
    )
    if include_unchanged:
        sampled.unchanged = _sample(result.unchanged, n, seed)
    return sampled


def sample_fraction(
    result: DiffResult,
    frac: float = 0.1,
    seed: Optional[int] = None,
) -> SampleResult:
    """Sample a *frac* fraction of rows from each change category."""
    if not (0.0 < frac <= 1.0):
        raise SamplerError(f"frac must be in (0, 1], got {frac}")
    def _frac_n(rows: List[Dict]) -> int:
        return max(1, int(len(rows) * frac)) if rows else 0

    return SampleResult(
        added=_sample(result.added, _frac_n(result.added), seed) if result.added else [],
        removed=_sample(result.removed, _frac_n(result.removed), seed) if result.removed else [],
        modified=_sample(result.modified, _frac_n(result.modified), seed) if result.modified else [],
    )
