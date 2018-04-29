import pytest
import json
import hyperjson
import string
from io import StringIO

simple_types = [1, 1.0, -1, None, "str", True]


@pytest.mark.parametrize("payload", simple_types)
def test_simple_types(payload):
    assert json.dumps(payload) == hyperjson.dumps(payload)


def strip_whitespace(a):
    """
    Compare two base strings, disregarding whitespace
    Adapted from https://github.com/dsindex/blog/wiki/%5Bpython%5D-string-compare-disregarding-white-space
    """
    WHITE_MAP = dict.fromkeys(ord(c) for c in string.whitespace)
    return a.translate(WHITE_MAP)


dicts = [
    {"a": 1, "b": 2},
    {1: "a", 2: "b"},
    {"complex": [4, 5, 6]},
    {"complex": [1, (23, 42)]}
]


@pytest.mark.parametrize("d", dicts)
def test_dict(d):
    assert strip_whitespace(json.dumps(
        d)) == strip_whitespace(hyperjson.dumps(d))


def test_dump():
    sio = StringIO()
    hyperjson.dump(['streaming API'], sio)
    assert sio.getvalue() == '["streaming API"]'
