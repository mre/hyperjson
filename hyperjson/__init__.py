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
