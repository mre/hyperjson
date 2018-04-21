from . import _hyperjson


def loads(s, encoding=None):
    """
    A shim around the Rust implementation
    TODO: Add remaining parameters of loads.
    See https://docs.python.org/3/library/json.html
    """
    return _hyperjson.loads(s, encoding)


def load(fp):
    """
    TODO: Add remaining parameters of loads.
    See https://docs.python.org/3/library/json.html
    """
    return _hyperjson.load(fp)
