import pytest
import json
import hyperjson
import io


def test_load():
    obj = io.StringIO(u'["streaming API"]')
    assert json.load(obj) == hyperjson.load(obj)


def test_load_invalid_reader():
    with pytest.raises(TypeError):
        hyperjson.load("{}", '')
