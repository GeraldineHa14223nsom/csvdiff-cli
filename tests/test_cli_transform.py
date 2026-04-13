"""Integration tests for the transform CLI sub-command."""

from __future__ import annotations

import io
import types

import pytest

from csvdiff.cli_transform import cmd_transform


def _make_args(
    csv_text: str,
    transform: list | None = None,
    rename: list | None = None,
) -> types.SimpleNamespace:
    return types.SimpleNamespace(
        input=io.StringIO(csv_text),
        output=io.StringIO(),
        transform=transform or [],
        rename=rename or [],
    )


SAMPLE = "id,name,score\n1,Alice,42\n2,Bob,7\n"


def test_transform_upper_name():
    args = _make_args(SAMPLE, transform=["name=upper"])
    rc = cmd_transform(args)
    assert rc == 0
    out = args.output.getvalue()
    assert "ALICE" in out
    assert "BOB" in out


def test_transform_lower_name():
    args = _make_args(SAMPLE, transform=["name=lower"])
    rc = cmd_transform(args)
    assert rc == 0
    assert "alice" in args.output.getvalue()


def test_rename_column():
    args = _make_args(SAMPLE, rename=["name=full_name"])
    rc = cmd_transform(args)
    assert rc == 0
    out = args.output.getvalue()
    assert "full_name" in out
    assert ",name," not in out


def test_transform_and_rename_combined():
    args = _make_args(SAMPLE, transform=["name=upper"], rename=["name=full_name"])
    rc = cmd_transform(args)
    assert rc == 0
    out = args.output.getvalue()
    assert "ALICE" in out
    assert "full_name" in out


def test_unknown_transform_returns_1():
    args = _make_args(SAMPLE, transform=["name=bogus"])
    rc = cmd_transform(args)
    assert rc == 1


def test_bad_value_returns_1():
    csv_text = "id,score\n1,not_a_number\n"
    args = _make_args(csv_text, transform=["score=int"])
    rc = cmd_transform(args)
    assert rc == 1


def test_malformed_mapping_returns_2():
    args = _make_args(SAMPLE, transform=["nameUPPER"])  # missing '='
    rc = cmd_transform(args)
    assert rc == 2


def test_empty_csv_returns_0():
    args = _make_args("id,name\n")
    rc = cmd_transform(args)
    assert rc == 0


def test_output_has_header():
    args = _make_args(SAMPLE)
    cmd_transform(args)
    first_line = args.output.getvalue().splitlines()[0]
    assert first_line == "id,name,score"
