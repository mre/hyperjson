# coding=UTF-8
from __future__ import print_function, unicode_literals
import six
from six.moves import range, zip

import calendar
import functools
import decimal
import json
import math
import time
import sys
import string

# Workaround for https://github.com/PyO3/pyo3/issues/171
from json import JSONDecodeError

if six.PY2:
    import unittest2 as unittest
else:
    import unittest

import hyperjson

json_unicode = hyperjson.dumps if six.PY3 else functools.partial(
    hyperjson.dumps, encoding="utf-8")


def ignore_whitespace(a):
    """
    Compare two base strings, disregarding whitespace
    Adapted from https://github.com/dsindex/blog/wiki/%5Bpython%5D-string-compare-disregarding-white-space
    """
    WHITE_MAP = dict.fromkeys(ord(c) for c in string.whitespace)
    return a.translate(WHITE_MAP)


class UltraJSONTests(unittest.TestCase):
    @unittest.skip("module 'json': TypeError: Object of type 'Decimal' is not JSON serializable")
    def test_encodeDecimal(self):
        sut = decimal.Decimal("1337.1337")
        encoded = hyperjson.dumps(sut)
        print(encoded)
        decoded = hyperjson.loads(encoded)
        print(decoded)
        self.assertEqual(decoded, 1337.1337)

    @unittest.skip("module 'json' does not support 'encode_html_chars'")
    def test_encodeStringConversion(self):
        input = "A string \\ / \b \f \n \r \t </script> &"
        not_html_encoded = '"A string \\\\ / \\b \\f \\n \\r \\t </script> &"'
        html_encoded = '"A string \\\\ \\/ \\b \\f \\n \\r \\t \\u003c\\/script\\u003e \\u0026"'
        not_slashes_escaped = '"A string \\\\ / \\b \\f \\n \\r \\t </script> &"'

        def helper(expected_output, **encode_kwargs):
            output = hyperjson.dumps(input, **encode_kwargs)
            self.assertEqual(output, expected_output)
            if encode_kwargs.get('escape_forward_slashes', True):
                self.assertEqual(input, hyperjson.loads(output))

        # Default behavior assumes encode_html_chars=False.
        helper(not_html_encoded, ensure_ascii=True)
        helper(not_html_encoded, ensure_ascii=False)

        # Make sure explicit encode_html_chars=False works.
        helper(not_html_encoded, ensure_ascii=True, encode_html_chars=False)
        helper(not_html_encoded, ensure_ascii=False, encode_html_chars=False)

        # Make sure explicit encode_html_chars=True does the encoding.
        helper(html_encoded, ensure_ascii=True, encode_html_chars=True)
        helper(html_encoded, ensure_ascii=False, encode_html_chars=True)

        # Do escape forward slashes if disabled.
        helper(not_slashes_escaped, escape_forward_slashes=False)

    @unittest.skip("module 'json' does not support 'encode_html_chars'")
    def testWriteEscapedString(self):
        self.assertEqual('"\\u003cimg src=\'\\u0026amp;\'\\/\\u003e"',
                         hyperjson.dumps("<img src='&amp;'/>", encode_html_chars=True))

    def test_doubleLongIssue(self):
        sut = {'a': -4342969734183514}
        encoded = hyperjson.dumps(sut)
        decoded = hyperjson.loads(encoded)
        self.assertEqual(sut, decoded)
        encoded = hyperjson.dumps(sut)
        decoded = hyperjson.loads(encoded)
        self.assertEqual(sut, decoded)

    def test_doubleLongDecimalIssue(self):
        sut = {'a': -12345678901234.56789012}
        encoded = hyperjson.dumps(sut)
        decoded = hyperjson.loads(encoded)
        self.assertEqual(sut, decoded)
        encoded = hyperjson.dumps(sut)
        decoded = hyperjson.loads(encoded)
        self.assertEqual(sut, decoded)

    def test_encodeDecodeLongDecimal(self):
        sut = {'a': -528656961.4399388}
        encoded = hyperjson.dumps(sut)
        hyperjson.loads(encoded)

    def test_decimalDecodeTest(self):
        sut = {'a': 4.56}
        encoded = hyperjson.dumps(sut)
        decoded = hyperjson.loads(encoded)
        self.assertAlmostEqual(sut[u'a'], decoded[u'a'])

    def test_encodeDictWithUnicodeKeys(self):
        input = {"key1": "value1", "key1": "value1", "key1": "value1",
                 "key1": "value1", "key1": "value1", "key1": "value1"}
        hyperjson.dumps(input)

        input = {"بن": "value1", "بن": "value1", "بن": "value1",
                 "بن": "value1", "بن": "value1", "بن": "value1", "بن": "value1"}
        hyperjson.dumps(input)

    def test_encodeDoubleConversion(self):
        input = math.pi
        output = hyperjson.dumps(input)
        self.assertEqual(round(input, 5), round(hyperjson.loads(output), 5))
        self.assertEqual(round(input, 5), round(hyperjson.loads(output), 5))

    def test_encodeWithDecimal(self):
        input = 1.0
        output = hyperjson.dumps(input)
        self.assertEqual(output, "1.0")

    def test_encodeDoubleNegConversion(self):
        input = -math.pi
        output = hyperjson.dumps(input)

        self.assertEqual(round(input, 5), round(hyperjson.loads(output), 5))
        self.assertEqual(round(input, 5), round(hyperjson.loads(output), 5))

    def test_encodeArrayOfNestedArrays(self):
        input = [[[[]]]] * 20
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        #self.assertEqual(output, hyperjson.dumps(input))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeArrayOfDoubles(self):
        input = [31337.31337, 31337.31337, 31337.31337, 31337.31337] * 10
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        #self.assertEqual(output, hyperjson.dumps(input))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeStringConversion2(self):
        input = "A string \\ / \b \f \n \r \t"
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(output, '"A string \\\\ / \\b \\f \\n \\r \\t"')
        self.assertEqual(input, hyperjson.loads(output))

    def test_decodeUnicodeConversion(self):
        pass

    def test_encodeUnicodeConversion1(self):
        input = "Räksmörgås اسامة بن محمد بن عوض بن لادن"
        enc = hyperjson.dumps(input)
        dec = hyperjson.loads(enc)
        self.assertEqual(enc, json_unicode(input))
        self.assertEqual(dec, hyperjson.loads(enc))

    def test_encodeControlEscaping(self):
        input = "\x19"
        enc = hyperjson.dumps(input)
        dec = hyperjson.loads(enc)
        self.assertEqual(input, dec)
        self.assertEqual(enc, json_unicode(input))

    def test_encodeUnicodeConversion2(self):
        input = "\xe6\x97\xa5\xd1\x88"
        enc = hyperjson.dumps(input)
        dec = hyperjson.loads(enc)
        self.assertEqual(enc, json_unicode(input))
        self.assertEqual(dec, hyperjson.loads(enc))

    def test_encodeUnicodeSurrogatePair(self):
        input = "\xf0\x90\x8d\x86"
        enc = hyperjson.dumps(input)
        dec = hyperjson.loads(enc)

        self.assertEqual(enc, json_unicode(input))
        self.assertEqual(dec, hyperjson.loads(enc))

    def test_encodeUnicode4BytesUTF8(self):
        input = "\xf0\x91\x80\xb0TRAILINGNORMAL"
        enc = hyperjson.dumps(input)
        dec = hyperjson.loads(enc)

        self.assertEqual(enc, json_unicode(input))
        self.assertEqual(dec, hyperjson.loads(enc))

    def test_encodeUnicode4BytesUTF8Highest(self):
        input = "\xf3\xbf\xbf\xbfTRAILINGNORMAL"
        enc = hyperjson.dumps(input)
        dec = hyperjson.loads(enc)

        self.assertEqual(enc, json_unicode(input))
        self.assertEqual(dec, hyperjson.loads(enc))

    # Characters outside of Basic Multilingual Plane(larger than
    # 16 bits) are represented as \UXXXXXXXX in python but should be encoded
    # as \uXXXX\uXXXX in hyperjson.
    def testEncodeUnicodeBMP(self):
        s = '\U0001f42e\U0001f42e\U0001F42D\U0001F42D'  # 🐮🐮🐭🐭
        encoded = hyperjson.dumps(s)
        encoded_json = hyperjson.dumps(s)

        if len(s) == 4:
            self.assertEqual(len(encoded), len(s) * 12 + 2)
        else:
            self.assertEqual(len(encoded), len(s) * 6 + 2)

        self.assertEqual(encoded, encoded_json)
        decoded = hyperjson.loads(encoded)
        self.assertEqual(s, decoded)

        # hyperjson outputs an UTF-8 encoded str object
        if six.PY3:
            encoded = hyperjson.dumps(s, ensure_ascii=False)
        else:
            encoded = hyperjson.dumps(s, ensure_ascii=False).decode("utf-8")

        # json outputs an unicode object
        encoded_json = hyperjson.dumps(s, ensure_ascii=False)
        self.assertEqual(len(encoded), len(s) + 2)  # original length + quotes
        self.assertEqual(encoded, encoded_json)
        decoded = hyperjson.loads(encoded)
        self.assertEqual(s, decoded)

    def testEncodeSymbols(self):
        s = '\u273f\u2661\u273f'  # ✿♡✿
        encoded = hyperjson.dumps(s)
        encoded_json = hyperjson.dumps(s)
        self.assertEqual(len(encoded), len(s) * 6 + 2)  # 6 characters + quotes
        self.assertEqual(encoded, encoded_json)
        decoded = hyperjson.loads(encoded)
        self.assertEqual(s, decoded)

        # hyperjson outputs an UTF-8 encoded str object
        if six.PY3:
            encoded = hyperjson.dumps(s, ensure_ascii=False)
        else:
            encoded = hyperjson.dumps(s, ensure_ascii=False).decode("utf-8")

        # json outputs an unicode object
        encoded_json = hyperjson.dumps(s, ensure_ascii=False)
        self.assertEqual(len(encoded), len(s) + 2)  # original length + quotes
        self.assertEqual(encoded, encoded_json)
        decoded = hyperjson.loads(encoded)
        self.assertEqual(s, decoded)

    def test_encodeArrayInArray(self):
        input = [[[[]]]]
        output = hyperjson.dumps(input)

        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(output, hyperjson.dumps(input))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeIntConversion(self):
        input = 31337
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(output, hyperjson.dumps(input))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeIntNegConversion(self):
        input = -31337
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(output, hyperjson.dumps(input))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeLongNegConversion(self):
        input = -9223372036854775808
        output = hyperjson.dumps(input)

        hyperjson.loads(output)
        hyperjson.loads(output)

        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(output, hyperjson.dumps(input))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeListConversion(self):
        input = [1, 2, 3, 4]
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeDictConversion(self):
        input = {"k1": 1, "k2": 2, "k3": 3, "k4": 4}
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeNoneConversion(self):
        input = None
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(output, hyperjson.dumps(input))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeTrueConversion(self):
        input = True
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(output, hyperjson.dumps(input))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeFalseConversion(self):
        input = False
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(output, hyperjson.dumps(input))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeToUTF8(self):
        input = b"\xe6\x97\xa5\xd1\x88"
        if six.PY3:
            input = input.decode('utf-8')
        enc = hyperjson.dumps(input, ensure_ascii=False)
        dec = hyperjson.loads(enc)
        self.assertEqual(enc, hyperjson.dumps(input, ensure_ascii=False))
        self.assertEqual(dec, hyperjson.loads(enc))

    def test_decodeFromUnicode(self):
        input = "{\"obj\": 31337}"
        dec1 = hyperjson.loads(input)
        dec2 = hyperjson.loads(str(input))
        self.assertEqual(dec1, dec2)

    @unittest.skip("module 'json' has no attribute 'encode'")
    def test_encodeRecursionMax(self):
        # 8 is the max recursion depth
        class O2:
            member = 0

            def toDict(self):
                return {"member": self.member}

        class O1:
            member = 0

            def toDict(self):
                return {"member": self.member}

        input = O1()
        input.member = O2()
        input.member.member = input
        self.assertRaises(OverflowError, hyperjson.dumps, input)

    @unittest.skip("OverflowError not raised by dumps")
    def test_encodeDoubleNan(self):
        input = float('nan')
        self.assertRaises(OverflowError, hyperjson.dumps, input)

    @unittest.skip("OverflowError not raised by dumps")
    def test_encodeDoubleInf(self):
        input = float('inf')
        self.assertRaises(OverflowError, hyperjson.dumps, input)

    @unittest.skip("OverflowError not raised by dumps")
    def test_encodeDoubleNegInf(self):
        input = -float('inf')
        self.assertRaises(OverflowError, hyperjson.dumps, input)

    @unittest.skipIf(sys.version_info < (2, 7), "No Ordered dict in < 2.7")
    @unittest.skip("Ignore for now, as I'm not sure wether the extra overhead in fixing this test is worth it")
    def test_encodeOrderedDict(self):
        from collections import OrderedDict
        input = OrderedDict([(1, 1), (0, 0), (8, 8), (2, 2)])
        self.assertEqual('{"1":1,"0":0,"8":8,"2":2}',
                         ignore_whitespace(hyperjson.dumps(input)))

    def test_decodeJibberish(self):
        input = "fdsa sda v9sa fdsa"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeBrokenArrayStart(self):
        input = "["
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeBrokenObjectStart(self):
        input = "{"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeBrokenArrayEnd(self):
        input = "]"
        self.assertRaises(ValueError, hyperjson.loads, input)

    @unittest.skip("Currently we return a ValueError, but we should return a RecursionError")
    def test_decodeArrayDepthTooBig(self):
        input = '[' * (1024 * 1024)
        self.assertRaises(RecursionError, hyperjson.loads, input)

    def test_decodeBrokenObjectEnd(self):
        input = "}"
        self.assertRaises(ValueError, hyperjson.loads, input)

    @unittest.skip("Skip for now because it clutters the screen with debug output")
    def test_decodeObjectDepthTooBig(self):
        input = '{' * (1024 * 1024)
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeStringUnterminated(self):
        input = "\"TESTING"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeStringUntermEscapeSequence(self):
        input = "\"TESTING\\\""
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeStringBadEscape(self):
        input = "\"TESTING\\\""
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeTrueBroken(self):
        input = "tru"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeFalseBroken(self):
        input = "fa"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeNullBroken(self):
        input = "n"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeBrokenDictKeyTypeLeakTest(self):
        input = '{{1337:""}}'
        for x in range(1000):
            self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeBrokenDictLeakTest(self):
        input = '{{"key":"}'
        for x in range(1000):
            self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeBrokenListLeakTest(self):
        input = '[[[true'
        for x in range(1000):
            self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeDictWithNoKey(self):
        input = "{{{{31337}}}}"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeDictWithNoColonOrValue(self):
        input = "{{{{\"key\"}}}}"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeDictWithNoValue(self):
        input = "{{{{\"key\":}}}}"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeNumericIntPos(self):
        input = "31337"
        self.assertEqual(31337, hyperjson.loads(input))

    def test_decodeNumericIntNeg(self):
        input = "-31337"
        self.assertEqual(-31337, hyperjson.loads(input))

    @unittest.skip("json module has no encode method")
    def test_encodeUnicode4BytesUTF8Fail(self):
        input = b"\xfd\xbf\xbf\xbf\xbf\xbf"
        self.assertRaises(OverflowError, hyperjson.dumps, input)

    def test_encodeNullCharacter(self):
        input = "31337 \x00 1337"
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(output, hyperjson.dumps(input))
        self.assertEqual(input, hyperjson.loads(output))

        input = "\x00"
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(output, hyperjson.dumps(input))
        self.assertEqual(input, hyperjson.loads(output))

        self.assertEqual('"  \\u0000\\r\\n "',
                         hyperjson.dumps("  \u0000\r\n "))

    def test_decodeNullCharacter(self):
        input = "\"31337 \\u0000 31337\""
        self.assertEqual(hyperjson.loads(input), hyperjson.loads(input))

    def test_encodeListLongConversion(self):
        input = [9223372036854775807, 9223372036854775807, 9223372036854775807,
                 9223372036854775807, 9223372036854775807, 9223372036854775807]
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeListLongUnsignedConversion(self):
        input = [18446744073709551615,
                 18446744073709551615, 18446744073709551615]
        output = hyperjson.dumps(input)

        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeLongConversion(self):
        input = 9223372036854775807
        output = hyperjson.dumps(input)
        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(output, hyperjson.dumps(input))
        self.assertEqual(input, hyperjson.loads(output))

    def test_encodeLongUnsignedConversion(self):
        input = 18446744073709551615
        output = hyperjson.dumps(input)
        print(output)

        self.assertEqual(input, hyperjson.loads(output))
        self.assertEqual(output, hyperjson.dumps(input))
        self.assertEqual(input, hyperjson.loads(output))

    def test_numericIntExp(self):
        input = "1337E40"
        output = hyperjson.loads(input)
        self.assertEqual(output, hyperjson.loads(input))

    def test_numericIntFrcExp(self):
        input = "1.337E40"
        output = hyperjson.loads(input)
        self.assertEqual(output, hyperjson.loads(input))

    def test_decodeNumericIntExpEPLUS(self):
        input = "1337E+9"
        output = hyperjson.loads(input)
        self.assertEqual(output, hyperjson.loads(input))

    def test_decodeNumericIntExpePLUS(self):
        input = "1.337e+40"
        output = hyperjson.loads(input)
        self.assertEqual(output, hyperjson.loads(input))

    def test_decodeNumericIntExpE(self):
        input = "1337E40"
        output = hyperjson.loads(input)
        self.assertEqual(output, hyperjson.loads(input))

    def test_decodeNumericIntExpe(self):
        input = "1337e40"
        output = hyperjson.loads(input)
        self.assertEqual(output, hyperjson.loads(input))

    def test_decodeNumericIntExpEMinus(self):
        input = "1.337E-4"
        output = hyperjson.loads(input)
        self.assertEqual(output, hyperjson.loads(input))

    def test_decodeNumericIntExpeMinus(self):
        input = "1.337e-4"
        output = hyperjson.loads(input)
        self.assertEqual(output, hyperjson.loads(input))

    def test_dumpToFile(self):
        f = six.StringIO()
        hyperjson.dump([1, 2, 3], f)
        self.assertEqual("[1,2,3]", f.getvalue())

    def test_dumpToFileLikeObject(self):
        class filelike:
            def __init__(self):
                self.bytes = ''

            def write(self, bytes):
                self.bytes += bytes

        f = filelike()
        hyperjson.dump([1, 2, 3], f)
        self.assertEqual("[1,2,3]", f.bytes)

    def test_dumpFileArgsError(self):
        self.assertRaises(AttributeError, hyperjson.dump, [], '')

    def test_loadFile(self):
        f = six.StringIO("[1,2,3,4]")
        self.assertEqual([1, 2, 3, 4], hyperjson.load(f))

    def test_loadFileLikeObject(self):
        class filelike:
            def read(self):
                try:
                    self.end
                except AttributeError:
                    self.end = True
                    return "[1,2,3,4]"

        f = filelike()
        self.assertEqual([1, 2, 3, 4], hyperjson.load(f))

    def test_loadFileArgsError(self):
        self.assertRaises(AttributeError, hyperjson.load, "[]")

    def test_version(self):
        if six.PY2:
            self.assertRegexpMatches(
                hyperjson.__version__, r'^\d+\.\d+(\.\d+)?$', "hyperjson.__version__ must be a string like '1.4.0'")
        else:
            self.assertRegex(hyperjson.__version__, r'^\d+\.\d+(\.\d+)?$',
                             "hyperjson.__version__ must be a string like '1.4.0'")

    @unittest.skip("OverflowError not raised by dumps")
    def test_encodeNumericOverflow(self):
        self.assertRaises(OverflowError, hyperjson.dumps,
                          12839128391289382193812939)

    def test_decodeNumberWith32bitSignBit(self):
        # Test that numbers that fit within 32 bits but would have the
        # sign bit set (2**31 <= x < 2**32) are decoded properly.
        docs = (
            '{"id": 3590016419}',
            '{"id": %s}' % 2**31,
            '{"id": %s}' % 2**32,
            '{"id": %s}' % ((2**32)-1),
        )
        results = (3590016419, 2**31, 2**32, 2**32-1)
        for doc, result in zip(docs, results):
            self.assertEqual(hyperjson.loads(doc)['id'], result)

    @unittest.skip("module 'json': TypeError: Object of type 'bytes' is not JSON serializable")
    def test_encodeBigEscape(self):
        for x in range(10):
            if six.PY3:
                base = '\u00e5'.encode('utf-8')
            else:
                base = "\xc3\xa5"
            input = base * 1024 * 1024 * 2
            hyperjson.dumps(input)

    def test_decodeBigEscape(self):
        for x in range(10):
            if six.PY3:
                base = '\u00e5'.encode('utf-8')
                quote = "\"".encode()
            else:
                base = "\xc3\xa5"
                quote = "\""
            input = quote + (base * 1024 * 1024 * 2) + quote
            hyperjson.loads(input)

    @unittest.skip("ujson specific, see github.com/esnme/ultrajson/issues/104")
    def test_toDict(self):
        d = {"key": 31337}

        class DictTest:
            def toDict(self):
                return d

            def __json__(self):
                return '"json defined"'  # Fallback and shouldn't be called.

        o = DictTest()
        output = hyperjson.dumps(o)
        dec = hyperjson.loads(output)
        self.assertEqual(dec, d)

    @unittest.skip("module 'json' does not support '__json__'")
    def test_object_with_json(self):
        # If __json__ returns a string, then that string
        # will be used as a raw JSON snippet in the object.
        output_text = 'this is the correct output'

        class JSONTest:
            def __json__(self):
                return '"' + output_text + '"'

        d = {u'key': JSONTest()}
        output = hyperjson.dumps(d)
        dec = hyperjson.loads(output)
        self.assertEqual(dec, {u'key': output_text})

    @unittest.skip("Not supported by json module, only by ujson and simplehyperjson. See https://github.com/simplejson/simplejson/issues/52")
    def test_object_with_json_unicode(self):
        # If __json__ returns a string, then that string
        # will be used as a raw JSON snippet in the object.
        output_text = u'this is the correct output'

        class JSONTest:
            def __json__(self):
                return u'"' + output_text + u'"'

        d = {u'key': JSONTest()}
        output = hyperjson.dumps(d)
        dec = hyperjson.loads(output)
        self.assertEqual(dec, {u'key': output_text})

    @unittest.skip("module 'json' does not support '__json__'")
    def test_object_with_complex_json(self):
        # If __json__ returns a string, then that string
        # will be used as a raw JSON snippet in the object.
        obj = {u'foo': [u'bar', u'baz']}

        class JSONTest:
            def __json__(self):
                return hyperjson.dumps(obj)

        d = {u'key': JSONTest()}
        output = hyperjson.dumps(d)
        dec = hyperjson.loads(output)
        self.assertEqual(dec, {u'key': obj})

    @unittest.skip("module 'json' has no attribute 'encode'")
    def test_object_with_json_type_error(self):
        # __json__ must return a string, otherwise it should raise an error.
        for return_value in (None, 1234, 12.34, True, {}):
            class JSONTest:
                def __json__(self):
                    return return_value

            d = {u'key': JSONTest()}
            self.assertRaises(TypeError, hyperjson.dumps, d)

    @unittest.skip("module 'json' has no attribute 'encode'")
    def test_object_with_json_attribute_error(self):
        # If __json__ raises an error, make sure python actually raises it.
        class JSONTest:
            def __json__(self):
                raise AttributeError

        d = {u'key': JSONTest()}
        self.assertRaises(AttributeError, hyperjson.dumps, d)

    def test_decodeArrayTrailingCommaFail(self):
        input = "[31337,]"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeArrayLeadingCommaFail(self):
        input = "[,31337]"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeArrayOnlyCommaFail(self):
        input = "[,]"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeArrayUnmatchedBracketFail(self):
        input = "[]]"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeArrayEmpty(self):
        input = "[]"
        obj = hyperjson.loads(input)
        self.assertEqual([], obj)

    def test_decodeArrayDict(self):
        input = "{}"
        obj = hyperjson.loads(input)
        self.assertEqual({}, obj)

    def test_decodeArrayOneItem(self):
        input = "[31337]"
        hyperjson.loads(input)

    def test_decodeLongUnsignedValue(self):
        input = "18446744073709551615"
        hyperjson.loads(input)

    @unittest.skip("module 'json': ValueError not raised by dumps")
    def test_decodeBigValue(self):
        input = "9223372036854775807"
        hyperjson.loads(input)

    def test_decodeSmallValue(self):
        input = "-9223372036854775808"
        hyperjson.loads(input)

    @unittest.skip("module 'json': ValueError not raised by dumps")
    def test_decodeTooBigValue(self):
        input = "18446744073709551616"
        self.assertRaises(ValueError, hyperjson.loads, input)

    @unittest.skip("module 'json': ValueError not raised by dumps")
    def test_decodeTooSmallValue(self):
        input = "-90223372036854775809"
        self.assertRaises(ValueError, hyperjson.loads, input)

    @unittest.skip("module 'json': Value error not raised by dumps")
    def test_decodeVeryTooBigValue(self):
        input = "18446744073709551616"
        self.assertRaises(ValueError, hyperjson.loads, input)

    @unittest.skip("module 'json': Value error not raised by dumps")
    def test_decodeVeryTooSmallValue(self):
        input = "-90223372036854775809"
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeWithTrailingWhitespaces(self):
        input = "{}\n\t "
        hyperjson.loads(input)

    def test_decodeWithTrailingNonWhitespaces(self):
        print(dir(hyperjson))
        input = "{}\n\t a"
        self.assertRaises(JSONDecodeError, hyperjson.loads, input)

    @unittest.skip("module 'json': ValueError not raised by dumps")
    def test_decodeArrayWithBigInt(self):
        input = '[18446744073709551616]'
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_decodeFloatingPointAdditionalTests(self):
        self.assertEqual(-1.1234567893, hyperjson.loads("-1.1234567893"))
        self.assertEqual(-1.234567893, hyperjson.loads("-1.234567893"))
        self.assertEqual(-1.34567893, hyperjson.loads("-1.34567893"))
        self.assertEqual(-1.4567893, hyperjson.loads("-1.4567893"))
        self.assertEqual(-1.567893, hyperjson.loads("-1.567893"))
        self.assertEqual(-1.67893, hyperjson.loads("-1.67893"))
        self.assertEqual(-1.7893, hyperjson.loads("-1.7893"))
        self.assertEqual(-1.893, hyperjson.loads("-1.893"))
        self.assertEqual(-1.3, hyperjson.loads("-1.3"))

        self.assertEqual(1.1234567893, hyperjson.loads("1.1234567893"))
        self.assertEqual(1.234567893, hyperjson.loads("1.234567893"))
        self.assertEqual(1.34567893, hyperjson.loads("1.34567893"))
        self.assertEqual(1.4567893, hyperjson.loads("1.4567893"))
        self.assertEqual(1.567893, hyperjson.loads("1.567893"))
        self.assertEqual(1.67893, hyperjson.loads("1.67893"))
        self.assertEqual(1.7893, hyperjson.loads("1.7893"))
        self.assertEqual(1.893, hyperjson.loads("1.893"))
        self.assertEqual(1.3, hyperjson.loads("1.3"))

    def test_ReadBadObjectSyntax(self):
        input = '{"age", 44}'
        self.assertRaises(ValueError, hyperjson.loads, input)

    def test_ReadTrue(self):
        self.assertEqual(True, hyperjson.loads("true"))

    def test_ReadFalse(self):
        self.assertEqual(False, hyperjson.loads("false"))

    def test_ReadNull(self):
        self.assertEqual(None, hyperjson.loads("null"))

    def test_WriteTrue(self):
        self.assertEqual("true", hyperjson.dumps(True))

    def test_WriteFalse(self):
        self.assertEqual("false", hyperjson.dumps(False))

    def test_WriteNull(self):
        self.assertEqual("null", hyperjson.dumps(None))

    def test_ReadArrayOfSymbols(self):
        self.assertEqual([True, False, None],
                         hyperjson.loads(" [ true, false,null] "))

    def test_WriteArrayOfSymbolsFromList(self):
        self.assertEqual(ignore_whitespace("[true, false, null]"),
                         ignore_whitespace(hyperjson.dumps([True, False, None])))

    def test_WriteArrayOfSymbolsFromTuple(self):
        self.assertEqual(ignore_whitespace("[true, false, null]"),
                         ignore_whitespace(hyperjson.dumps((True, False, None))))

    #@unittest.skipIf(not six.PY3, "Only raises on Python 3")
    @unittest.skip("Panic in pyo3. See link below")
    def test_encodingInvalidUnicodeCharacter(self):
        """
        https://github.com/PyO3/pyo3/blob/master/src/objects/string.rs#L67
        """
        s = "\udc7f"
        self.assertRaises(UnicodeEncodeError, hyperjson.dumps, s)

    def test_sortKeys(self):
        data = {"a": 1, "c": 1, "b": 1, "e": 1, "f": 1, "d": 1}
        sortedKeys = hyperjson.dumps(data, sort_keys=True)
        self.assertEqual(
            sortedKeys, '{"a":1,"b":1,"c":1,"d":1,"e":1,"f":1}')


"""
def test_decodeNumericIntFrcOverflow(self):
input = "X.Y"
raise NotImplementedError("Implement this test!")
def test_decodeStringUnicodeEscape(self):
input = "\u3131"
raise NotImplementedError("Implement this test!")
def test_decodeStringUnicodeBrokenEscape(self):
input = "\u3131"
raise NotImplementedError("Implement this test!")
def test_decodeStringUnicodeInvalidEscape(self):
input = "\u3131"
raise NotImplementedError("Implement this test!")
def test_decodeStringUTF8(self):
input = "someutfcharacters"
raise NotImplementedError("Implement this test!")
"""

if __name__ == "__main__":
    unittest.main()

"""
# Use this to look for memory leaks
if __name__ == '__main__':
    from guppy import hpy
    hp = hpy()
    hp.setrelheap()
    while True:
        try:
            unittest.main()
        except SystemExit:
            pass
        heap = hp.heapu()
        print(heap)
"""
