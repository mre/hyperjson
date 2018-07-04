import hyperjson
import ujson
import sys
import random
import pytest
import simplejson
import yajl

LIBRARIES = [hyperjson, ujson, simplejson, yajl]


@pytest.mark.parametrize('lib', LIBRARIES, ids=lambda l: l.__name__)
def test_array_doubles(lib, benchmark):
    test_object = [sys.maxsize * random.random() for _ in range(256)]
    benchmark(lib.dumps, test_object)
