import pytest
import math

import json
import hyperjson
from io import StringIO


def test_loading_empty_value():
    with pytest.raises(ValueError):
        json.loads("")
    with pytest.raises(ValueError):
        hyperjson.loads("")


def test_loading_two_values():
    payload = '{"foo": "bar"}'
    with pytest.raises(LookupError):
        json.loads(payload, payload)
    with pytest.raises(LookupError):
        hyperjson.loads(payload, payload)


simple_types = ["1", "1.0", "-1", "null", '"str"', "true"]


@pytest.mark.parametrize("payload", simple_types)
def test_simple_types(payload):
    assert json.loads(payload) == hyperjson.loads(payload)


def test_special_floats():
    assert math.isnan(json.loads("NaN"))
    assert math.isnan(hyperjson.loads("NaN"))
    assert math.isinf(json.loads("Infinity"))
    assert math.isinf(hyperjson.loads("Infinity"))
    assert math.isinf(json.loads("-Infinity"))
    assert math.isinf(hyperjson.loads("-Infinity"))


def test_string_map():
    payload = '{"foo": "bar"}'
    assert json.loads(payload) == hyperjson.loads(payload)


def test_array():
    payload = '["foo", "bar"]'
    assert json.loads(payload) == hyperjson.loads(payload)


def test_loading_docs_example():
    """
    See https://docs.python.org/3/library/json.html
    """
    payload = '["foo", {"bar":["baz", null, 1.0, 2]}]'
    assert json.loads(payload) == hyperjson.loads(payload)


def test_load():
    from io import StringIO
    obj = StringIO(u'["streaming API"]')
    assert json.load(obj) == hyperjson.load(obj)
