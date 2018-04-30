import pytest
import hyperjson
from io import StringIO


def test_dump():
    sio = StringIO()
    hyperjson.dump(['streaming API'], sio)
    assert sio.getvalue() == '["streaming API"]'


def test_dump_invalid_writer():
    with pytest.raises(TypeError):
        hyperjson.dump([], '')
