"""Tests for csvdiff.sampler."""
import pytest

from csvdiff.core import DiffResult
from csvdiff.sampler import (
    SamplerError,
    SampleResult,
    _sample,
    sample_fraction,
    sample_result,
)


@pytest.fixture()
def result() -> DiffResult:
    added = [{"id": str(i), "v": "a"} for i in range(20)]
    removed = [{"id": str(i), "v": "r"} for i in range(15)]
    modified = [{"id": str(i), "v": "m"} for i in range(10)]
    unchanged = [{"id": str(i), "v": "u"} for i in range(5)]
    return DiffResult(added=added, removed=removed, modified=modified, unchanged=unchanged)


def test_sample_returns_n_items():
    rows = [{"id": str(i)} for i in range(50)]
    out = _sample(rows, 10, seed=42)
    assert len(out) == 10


def test_sample_returns_all_when_fewer_than_n():
    rows = [{"id": str(i)} for i in range(5)]
    out = _sample(rows, 10, seed=0)
    assert len(out) == 5


def test_sample_invalid_n_raises():
    with pytest.raises(SamplerError):
        _sample([{"id": "1"}], 0, seed=None)


def test_sample_result_respects_n(result):
    sr = sample_result(result, n=5, seed=0)
    assert len(sr.added) == 5
    assert len(sr.removed) == 5
    assert len(sr.modified) == 5


def test_sample_result_unchanged_excluded_by_default(result):
    sr = sample_result(result, n=5, seed=0)
    assert sr.unchanged == []


def test_sample_result_include_unchanged(result):
    sr = sample_result(result, n=3, seed=1, include_unchanged=True)
    assert len(sr.unchanged) == 3


def test_sample_result_invalid_n_raises(result):
    with pytest.raises(SamplerError):
        sample_result(result, n=-1)


def test_sample_result_deterministic(result):
    sr1 = sample_result(result, n=5, seed=99)
    sr2 = sample_result(result, n=5, seed=99)
    assert sr1.added == sr2.added
    assert sr1.removed == sr2.removed


def test_sample_fraction_basic(result):
    sr = sample_fraction(result, frac=0.5, seed=7)
    assert 1 <= len(sr.added) <= len(result.added)
    assert 1 <= len(sr.removed) <= len(result.removed)


def test_sample_fraction_invalid_raises(result):
    with pytest.raises(SamplerError):
        sample_fraction(result, frac=0.0)
    with pytest.raises(SamplerError):
        sample_fraction(result, frac=1.5)


def test_sample_fraction_empty_category():
    r = DiffResult(added=[], removed=[{"id": "1"}], modified=[], unchanged=[])
    sr = sample_fraction(r, frac=0.5)
    assert sr.added == []
    assert len(sr.removed) >= 1
