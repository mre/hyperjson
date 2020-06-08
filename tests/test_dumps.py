import json
import string
from io import StringIO

import hyperjson
import pytest


@pytest.fixture(params=["fp", "str"])
def dumps(request):
    if request.param == "fp":

        def dump(obj, *args, **kwargs):
            fp = StringIO()
            json.dump(obj, fp, *args, **kwargs)
            return fp.getvalue()

        return dump
    elif request.param == "str":
        return json.dumps


simple_types = [1, 1.0, -1, None, "str", True, False]


@pytest.mark.parametrize("payload", simple_types)
def test_simple_types(payload, dumps):
    assert dumps(payload) == dumps(payload)


def ignore_whitespace(a):
    """
    Compare two base strings, disregarding whitespace
    Adapted from https://github.com/dsindex/blog/wiki/%5Bpython%5D-string-compare-disregarding-white-space
    """
    WHITE_MAP = dict.fromkeys(ord(c) for c in string.whitespace)
    return a.translate(WHITE_MAP)


simple_dicts = [
    ({"a": 1, "b": 2}, ['{"a":1,"b":2}', '{"b":2,"a":1}']),
    ({1: "a", 2: "b"}, ['{"1":"a","2":"b"}', '{"2":"b","1":"a"}']),
]


@pytest.mark.parametrize("d,allowed", simple_dicts)
def test_simple_dicts(d, allowed, dumps):
    """
    Python dictionaries are guaranteed to be ordered in Python 3.6+,
    in Python <=3.5 they are not ordered.
    In Rust, HashMaps are not, but that's not a big deal
    because JSON also doesn't guarantee order.
    See https://stackoverflow.com/a/7214316/270334
    Therefore, we ignore ordering to avoid flaky tests.
    """
    actual = ignore_whitespace(dumps(d))
    assert actual in allowed


complex_dicts = [
    {"complex": [4, 5, 6]},
    {"complex": [1, (23, 42)]}
]


@pytest.mark.parametrize("d", complex_dicts)
def test_complex_dicts(d, dumps):
    assert ignore_whitespace(dumps(d)) == ignore_whitespace(dumps(d))


def test_dict_of_arrays_of_dict_string_int_pairs(dumps):
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
    assert hyperjson.loads(dumps(payload)) == payload


@pytest.mark.parametrize(
    "json_data,string_data,indent",
    (
        ("str", '"str"', 4),
        (True, "true", 4),
        (None, "null", 4),
        (5, "5", 4),
        ({}, "{}", 4),
        ([], "[]", 4),
        ([2], "[\n    2\n]", 4),
        ({"2": 3}, '{\n    "2": 3\n}', 4),
        ([[1], {"2": 3}], '[\n  [\n    1\n  ],\n  {\n    "2": 3\n  }\n]', 2),
        ({"a": [1], "d": {"2": 3}}, '{\n  "a": [\n    1\n  ],\n  "d": {\n    "2": 3\n  }\n}', 2),
    ),
    ids=(
        "0-level-str",
        "0-level-bool",
        "0-level-null",
        "0-level-number",
        "0-level-dict",
        "0-level-array",
        "1-level-array",
        "1-level-dict",
        "2-level-array",
        "2-level-dict",
    )
)
def test_indent(json_data, string_data, indent, dumps):
    assert dumps(json_data, indent=indent, sort_keys=True) == string_data


def test_sort(dumps):
    data = {"d": 1, "c": 1, "e": 1, "b": 1, "f": 1, "a": 1}
    sortedKeys = dumps(data, sort_keys=True)
    assert sortedKeys == '{"a": 1, "b": 1, "c": 1, "d": 1, "e": 1, "f": 1}'
