from cpython import PyTest, CTest, RustTest


# from http://json.org/JSON_checker/test/pass2.json
JSON = r'''
[[[[[[[[[[[[[[[[[[["Not too deep"]]]]]]]]]]]]]]]]]]]
'''

class _TestPass2:
    def test_parse(self):
        # test in/out equivalence and parsing
        res = self.loads(JSON)
        out = self.dumps(res)
        self.assertEqual(res, self.loads(out))


# class TestPyPass2(_TestPass2, PyTest): pass
# class TestCPass2(_TestPass2, CTest): pass
class TestRustPass2(_TestPass2, RustTest): pass
