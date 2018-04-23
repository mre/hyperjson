import pytest
import decimal
import hyperjson

"""
These are official json tests copied from
https://github.com/python/cpython/blob/cfa797c0681b7fef47cf93955fd06b54ddd09a7f/Lib/test/test_json/test_decode.py
and converted to pytest.
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


def test_empty_objects():
    assert hyperjson.loads('{}') == {}
    assert hyperjson.loads('[]') == []
    assert hyperjson.loads('""') == ""


"""
def test_object_pairs_hook(self):
    s = '{"xkd":1, "kcw":2, "art":3, "hxm":4, "qrt":5, "pad":6, "hoy":7}'
    p = [("xkd", 1), ("kcw", 2), ("art", 3), ("hxm", 4),
            ("qrt", 5), ("pad", 6), ("hoy", 7)]
    self.assertEqual(self.loads(s), eval(s))
    self.assertEqual(self.loads(s, object_pairs_hook=lambda x: x), p)
    self.assertEqual(self.json.load(StringIO(s),
                                    object_pairs_hook=lambda x: x), p)
    od = self.loads(s, object_pairs_hook=OrderedDict)
    self.assertEqual(od, OrderedDict(p))
    self.assertEqual(type(od), OrderedDict)
    # the object_pairs_hook takes priority over the object_hook
    self.assertEqual(self.loads(s, object_pairs_hook=OrderedDict,
                                object_hook=lambda x: None),
                        OrderedDict(p))
    # check that empty object literals work (see #17368)
    self.assertEqual(self.loads('{}', object_pairs_hook=OrderedDict),
                        OrderedDict())
    self.assertEqual(self.loads('{"empty": {}}',
                                object_pairs_hook=OrderedDict),
                        OrderedDict([('empty', OrderedDict())]))

"""


def test_decoder_optimizations():
    # Several optimizations were made that skip over calls to
    # the whitespace regex, so this test is designed to try and
    # exercise the uncommon cases. The array cases are already covered.
    rval = hyperjson.loads('{   "key"    :    "value"    ,  "k":"v"    }')
    assert rval == {"key": "value", "k": "v"}


def test_keys_reuse():
    s = '[{"a_key": 1, "b_\xe9": 2}, {"a_key": 3, "b_\xe9": 4}]'
    rval = hyperjson.loads(s)
    (a, b), (c, d) = sorted(rval[0]), sorted(rval[1])
    assert a == c
    assert b == d


"""
def test_extra_data(self):
    s = '[1, 2, 3]5'
    msg = 'Extra data'
    self.assertRaisesRegex(self.JSONDecodeError, msg, self.loads, s)


def test_invalid_escape(self):
    s = '["abc\\y"]'
    msg = 'escape'
    self.assertRaisesRegex(self.JSONDecodeError, msg, self.loads, s)


def test_invalid_input_type(self):
    msg = 'the JSON object must be str'
    for value in [1, 3.14, [], {}, None]:
        self.assertRaisesRegex(TypeError, msg, self.loads, value)


def test_string_with_utf8_bom(self):
    # see #18958
    bom_json = "[1,2,3]".encode('utf-8-sig').decode('utf-8')
    with self.assertRaises(self.JSONDecodeError) as cm:
        self.loads(bom_json)
    self.assertIn('BOM', str(cm.exception))
    with self.assertRaises(self.JSONDecodeError) as cm:
        self.json.load(StringIO(bom_json))
    self.assertIn('BOM', str(cm.exception))
    # make sure that the BOM is not detected in the middle of a string
    bom_in_str = '"{}"'.format(''.encode('utf-8-sig').decode('utf-8'))
    self.assertEqual(self.loads(bom_in_str), '\ufeff')
    self.assertEqual(self.json.load(StringIO(bom_in_str)), '\ufeff')
"""
