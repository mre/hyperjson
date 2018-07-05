import sys
import random
import pytest

benchmark = pytest.importorskip('pytest_benchmark')

doubles = []
numbers = []
unicode_strings = []
strings = []
booleans = []
list_dicts = []
dict_lists = {}

composite_object = {
    'words': """
        Lorem ipsum dolor sit amet, consectetur adipiscing
        elit. Mauris adipiscing adipiscing placerat.
        Vestibulum augue augue,
        pellentesque quis sollicitudin id, adipiscing.
        """,
    'list': list(range(200)),
    'dict': dict((str(i), 'a') for i in list(range(200))),
    'int': 100100100,
    'float': 100999.123456
}
for x in range(256):
    doubles.append(sys.maxsize * random.random())
    unicode_strings.append(
        "نظام الحكم سلطاني وراثي في الذكور من ذرية السيد تركي بن سعيد بن سلطان ويشترط فيمن يختار لولاية الحكم من بينهم ان يكون مسلما رشيدا عاقلا ًوابنا شرعيا لابوين عمانيين ")
    strings.append("A pretty long string which is in a list")
    booleans.append(True)

for y in range(100):
    arrays = []
    list_dicts.append({str(random.random()*20): int(random.random()*1000000)})

    for x in range(100):
        arrays.append({str(random.random() * 20): int(random.random()*1000000)})
        dict_lists[str(random.random() * 20)] = arrays

user = {
    "userId": 3381293,
    "age": 213,
    "username": "johndoe",
    "fullname": u"John Doe the Second",
    "isAuthorized": True,
    "liked": 31231.31231202,
    "approval": 31.1471,
    "jobs": [1, 2],
    "currJob": None
}

friends = [user, user, user, user, user, user, user, user]
complex_object = [
    [user, friends],  [user, friends],  [user, friends],
    [user, friends],  [user, friends],  [user, friends]
]
datasets = [('composite object', composite_object),
            ('256 doubles array', doubles),
            ('256 unicode array', unicode_strings),
            ('256 ascii array', strings),
            ('256 Trues array', booleans),
            ('100 dicts array', list_dicts),
            # ('100 arrays dict', dict_lists),
            ('complex object', complex_object),
            ]


@pytest.mark.benchmark(group='serialize')
@pytest.mark.parametrize('data', [d[1] for d in datasets], ids=[d[0] for d in datasets])
def test_dumps(contender, data, benchmark):
    benchmark(contender.dumps, data)


@pytest.mark.benchmark(group='deserialize')
@pytest.mark.parametrize('data', [d[1] for d in datasets], ids=[d[0] for d in datasets])
def test_loads(contender, data, benchmark):
    data = contender.dumps(data)
    benchmark(contender.loads, data)
