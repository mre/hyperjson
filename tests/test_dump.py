import pytest
import hyperjson
from io import StringIO
import json


def test_dump():
    sio = StringIO()
    hyperjson.dump(['streaming API'], sio)
    assert sio.getvalue() == '["streaming API"]'


def test_dump_invalid_writer():
    with pytest.raises(AttributeError):
        json.dump([], '')
    with pytest.raises(AttributeError):
        hyperjson.dump([], '')
