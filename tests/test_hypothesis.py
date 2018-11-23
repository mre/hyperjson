import hyperjson
import pytest
from hypothesis import given, assume, settings, strategies as st


# min, max: RFC 7159
st_int = st.integers(min_value=-(2**53)+1, max_value=(2**53)-1)
st_floats = st.floats(min_value=-(2**53)+1, max_value=(2**53)-1)

# st.floats would be nice, but then we need pytest.approx, which doesn't work with eg. text
st_json = st.recursive(st.booleans() | st.text() | st.none() | st_int  # | st_floats
                       , lambda children: st.lists(children) | st.dictionaries(st.text(), children))


@given(st_floats)
def test_floats(xs):
    assert hyperjson.loads(hyperjson.dumps(xs)) == pytest.approx(
        xs)  # fails when abs=0.05


@given(st.text())
def test_text(xs):
    assert hyperjson.loads(hyperjson.dumps(xs)) == xs


@given(st.booleans())
def test_bool(xs):
    assert hyperjson.loads(hyperjson.dumps(xs)) == xs


@given(st.none())
def test_none(xs):
    assert hyperjson.loads(hyperjson.dumps(xs)) == xs


@given(st.lists(st_int))
def test_list_integers(lst):
    assert hyperjson.loads(hyperjson.dumps(lst)) == lst


@given(st.lists(st.floats(min_value=-(2**53)+1, max_value=(2**53)-1)))
def test_list_floats(lst):
    assert hyperjson.loads(hyperjson.dumps(lst)) == pytest.approx(lst)


@given(st.lists(st.text()))
def test_list_text(lst):
    assert hyperjson.loads(hyperjson.dumps(lst)) == lst

@given(st.lists(st.one_of(st.none(), st.text())))
def test_list_mixed(lst):
    assert hyperjson.loads(hyperjson.dumps(
        lst)) == lst

@given(st.lists(st.one_of(st_int, st_floats)))
def test_list_mixed(lst):
    assert hyperjson.loads(hyperjson.dumps(
        lst)) == pytest.approx(lst)


@given(st_json)
def test_json_obj(j_obj):
    assert hyperjson.loads(hyperjson.dumps(j_obj)) == j_obj
