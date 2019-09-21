# based on https://github.com/lelit/python-rapidjson/blob/master/benchmarks/conftest.py
import hyperjson
from collections import namedtuple
from operator import attrgetter

Contender = namedtuple('Contender', 'name,dumps,loads')


def pytest_benchmark_group_stats(config, benchmarks, group_by):
    result = {}
    for bench in benchmarks:
        engine, data_kind = bench['param'].split('-')
        group = result.setdefault("%s: %s" % (data_kind, bench['group']), [])
        group.append(bench)
    return sorted(result.items())


def pytest_addoption(parser):
    parser.addoption('--compare', action='store_true',
                     help='compare against other JSON engines')


contenders = []

contenders.append(Contender('hyperjson',
                            hyperjson.dumps,
                            hyperjson.loads))
try:
    import simplejson
except ImportError:
    pass
else:
    contenders.append(Contender('simplejson',
                                simplejson.dumps,
                                simplejson.loads))
try:
    import ujson
except ImportError:
    pass
else:
    contenders.append(Contender('ujson',
                                ujson.dumps,
                                ujson.loads))
try:
    import yajl
except ImportError:
    pass
else:
    contenders.append(Contender('yajl',
                                yajl.dumps,
                                yajl.loads))

try:
    import rapidjson
except ImportError:
    pass
else:
    contenders.append(Contender('rapidjson',
                                rapidjson.dumps,
                                rapidjson.loads))

try:
    import orjson
except ImportError:
    pass
else:
    contenders.append(Contender('orjson',
                                orjson.dumps,
                                orjson.loads))


def pytest_generate_tests(metafunc):
    if 'contender' in metafunc.fixturenames:
        if metafunc.config.getoption('compare'):
            metafunc.parametrize('contender', contenders,
                                 ids=attrgetter('name'))
        else:
            metafunc.parametrize(
                'contender', contenders[:1], ids=attrgetter('name'))
