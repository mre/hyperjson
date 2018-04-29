import hyperjson


def test_docs():
    assert hyperjson.dumps([{"key": "value"}, 81, True]
                           ) == '[{"key":"value"},81,true]'
    assert hyperjson.loads("""[{"key": "value"}, 81, true]""") == [
        {u'key': u'value'}, 81, True]
