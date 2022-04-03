"""Miscellanous helpers."""

import collections
import re
from typing import Dict, Optional, Sequence, Tuple, TypeVar

T = TypeVar("T")
K = TypeVar("K")


def order_dict(
    d: Dict[Optional[K], T], keys: Sequence[Optional[K]]
) -> Dict[Optional[K], T]:
    """
    Produce an OrderedDict of `d`, but with the keys in `keys` order.

    Keys in `d` that don't appear in `keys` will be at the end in an
    undetermined order.
    """
    with_order = collections.OrderedDict()
    to_insert = set(d)
    for k in keys:
        if k not in to_insert:
            continue
        with_order[k] = d[k]
        to_insert.remove(k)

    for k in to_insert:
        with_order[k] = d[k]

    return with_order


def cut_at_line(text: str, marker: str) -> Tuple[str, str]:
    """
    Split text into two parts: up to the line with marker, and lines after.

    If `marker` isn't in the text, return ("", text)
    """
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if marker in line:
            return "".join(lines[: i + 1]), "".join(lines[i + 1 :])
    return ("", text)


VERSION_REGEX = r"""(?ix)   # based on https://peps.python.org/pep-0440/
    \b                      # at a word boundary
    v?                      # maybe a leading "v"
    (\d+!)?                 # maybe a version epoch
    \d+(\.\d+)+             # the meat of the version number: N.N.N
    (?P<pre>
        [-._]?[a-z]+\.?\d*
    )?                      # maybe a pre-release: .beta3
    ([-._][a-z]+\d*)*       # maybe post and dev releases
    (\+\w[\w.]*\w)?         # maybe a local version
    \b
    """


def extract_version(text: str) -> Optional[str]:
    """Find a version number in a text string."""
    m = re.search(VERSION_REGEX, text)
    if m:
        return m[0]
    return None


def is_prerelease_version(version: str) -> bool:  # noqa: D400
    """Is this version number a pre-release?"""
    m = re.fullmatch(VERSION_REGEX, version)
    assert m  # the version must be a valid version
    return bool(m["pre"])
