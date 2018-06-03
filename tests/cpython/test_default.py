from test.test_json import PyTest, CTest


class _TestDefault:
    def test_default(self):
        self.assertEqual(
            self.dumps(type, default=repr),
            self.dumps(repr(type)))


class TestPyDefault(_TestDefault, PyTest): pass
class TestCDefault(_TestDefault, CTest): pass
