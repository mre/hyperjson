import pytest
import decimal
import hyperjson

"""
These are official json tests copied from
https://github.com/python/cpython/blob/cfa797c0681b7fef47cf93955fd06b54ddd09a7f/Lib/test/test_json/test_decode.py
If you change them, consider sending a pull request to the upstream repo, too.
"""


def test_decimal():
    rval = hyperjson.loads('1.1', parse_float=decimal.Decimal)
    assert isinstance(rval, decimal.Decimal) == True
    assert pytest.approx(rval) == decimal.Decimal('1.1')


def test_float():
    rval = hyperjson.loads('1', parse_int=float)
    assert isinstance(rval, float)
    assert rval == 1.0
