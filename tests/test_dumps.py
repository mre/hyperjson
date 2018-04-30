import pytest
import json
import hyperjson
import string
from io import StringIO

simple_types = [1, 1.0, -1, None, "str", True]


@pytest.mark.parametrize("payload", simple_types)
def test_simple_types(payload):
    assert json.dumps(payload) == hyperjson.dumps(payload)


def ignore_whitespace(a):
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
    assert ignore_whitespace(json.dumps(
        d)) == ignore_whitespace(hyperjson.dumps(d))


def test_dict_of_arrays_of_dict_string_int_pairs():
    payload = {
        '9.865710069007799': [
            {
                '19.37384331792742': 315795
            }
        ],
        '5.076904844489237': [
            {
                '0.479301331636357': 460144
            }
        ]
    }
    # The order of elements is different when using hyperjson,
    # because of Rust's hashmap implementation.
    # assert ignore_whitespace(json.dumps(payload)) == ignore_whitespace(
    #     hyperjson.dumps(payload))
    assert hyperjson.loads(hyperjson.dumps(payload)) == payload
