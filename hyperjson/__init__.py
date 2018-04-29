from . import _hyperjson


def loads(s,
          *,
          encoding=None,
          cls=None,
          object_hook=None,
          parse_float=None,
          parse_int=None,
          parse_constant=None,
          object_pairs_hook=None,
          **kw):
    """
    A shim around the Rust implementation
    TODO: Add remaining parameters of loads.
    See https://docs.python.org/3/library/json.html
    """
    return _hyperjson.loads(s, encoding, cls, object_hook, parse_float, parse_int, parse_constant, object_hook, kw)


def load(fp):
    """
    TODO: Add remaining parameters of loads.
    See https://docs.python.org/3/library/json.html
    """
    return _hyperjson.load(fp)


# def dumps(obj, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, default=None, sort_keys=False, **kw):
#     return _hyperjson.dumps(obj, skipkeys, ensure_ascii, check_circular, allow_nan, cls, indent, separators, default, sort_keys, **kw)

def dumps(obj, **kw):
    return _hyperjson.dumps(obj, **kw)


def dump(obj, fp, **kw):
    return _hyperjson.dump(obj, fp, **kw)
