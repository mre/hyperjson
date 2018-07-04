# coding=UTF-8
# Taken from https://raw.githubusercontent.com/esnme/ultrajson/master/tests/benchmark.py

from __future__ import division, print_function, unicode_literals
import json
import os
import platform
import random
import sys
import timeit

import hyperjson

if sys.platform == 'win32':
    from colorama import init
    init()

USER = {"userId": 3381293, "age": 213, "username": "johndoe", "fullname": "John Doe the Second",
        "isAuthorized": True, "liked": 31231.31231202, "approval": 31.1471, "jobs": [1, 2], "currJob": None}
FRIENDS = [USER, USER, USER, USER, USER, USER, USER, USER]

decode_data = None
test_object = None
skip_lib_comparisons = False
if not skip_lib_comparisons:
    import ujson
    import simplejson
    import yajl

benchmark_results = []


# =============================================================================
# Logging benchmarking results.
# =============================================================================
def results_new_benchmark(name):
    benchmark_results.append((name, {}, {}))
    print(name)


def results_record_result(callback, is_encode, count):
    callback_name = callback.__name__
    library = callback_name.split("_")[-1]
    try:
        results = timeit.repeat("{}()".format(callback_name), "from __main__ import {}".format(
            callback_name), repeat=10, number=count)
        result = count / min(results)
    except TypeError as e:
        print(e)
        result = 0.0
    benchmark_results[-1][1 if is_encode else 2][library] = result

    print("{} {}: {:.02f} calls/sec".format(library,
                                            "encode" if is_encode else "decode", result))


def results_output_table():
    LIBRARIES = ("hyperjson", "ujson", "yajl", "simplejson", "json")
    ENDC = '\033[0m'
    GREEN = '\033[92m'

    uname_system, _, uname_release, uname_version, _, uname_processor = platform.uname()
    print()
    print("~~~~~~~~~~~~~")
    print("Test machine:")
    print("~~~~~~~~~~~~~")
    print()
    print(uname_system, uname_release, uname_processor, uname_version)
    print()

    column_widths = [max(len(r[0]) for r in benchmark_results)]
    for library in LIBRARIES:
        column_widths.append(max(10, len(library)))

    line = "+{}+".format("+".join("-"*(width + 2) for width in column_widths))
    columns = [" "*(width + 2) for width in column_widths]
    for i, library in enumerate(LIBRARIES):
        columns[i + 1] = (" " + library).ljust(column_widths[i + 1] + 2)
    print(line)
    print("|{}|".format("|".join(columns)))
    print(line.replace("-", "="))

    for name, encodes, decodes in benchmark_results:
        columns = [" " * (width + 2) for width in column_widths]
        columns[0] = (" " + name).ljust(column_widths[0] + 2)
        print("|{}|".format("|".join(columns)))
        print(line)

        columns = [None] * len(column_widths)
        columns[0] = " encode".ljust(column_widths[0] + 2)
        best = max([encodes[library] for library in LIBRARIES])
        for i, library in enumerate(LIBRARIES):
            if library in encodes:
                if encodes[library] == best:
                    s = GREEN
                else:
                    s = ''
                columns[i + 1] = s + "{:.2f} ".format(
                    encodes[library]).rjust(column_widths[i + 1] + 2) + ENDC
            else:
                columns[i + 1] = " "*(column_widths[i + 1] + 2)
        print("|{}|".format("|".join(columns)))
        print(line)

        if decodes:
            columns = [None] * len(column_widths)
            columns[0] = " decode".ljust(column_widths[0] + 2)
            best = max([decodes[library] for library in LIBRARIES])
            for i, library in enumerate(LIBRARIES):
                if library in decodes:
                    if decodes[library] == best:
                        s = GREEN
                    else:
                        s = ''
                    columns[i + 1] = s + "{:.2f} ".format(
                        decodes[library]).rjust(column_widths[i + 1] + 2) + ENDC
                else:
                    columns[i + 1] = " "*(column_widths[i + 1] + 2)
            print("|{}|".format("|".join(columns)))
            print(line)


# =============================================================================
# JSON encoding.
# =============================================================================
def dumps_with_hyperjson():
    hyperjson.dumps(test_object)


def dumps_with_json():
    json.dumps(test_object)


def dumps_with_simplejson():
    simplejson.dumps(test_object)


def dumps_with_ujson():
    ujson.dumps(test_object, ensure_ascii=False)


def dumps_with_yajl():
    yajl.dumps(test_object)


# =============================================================================
# JSON encoding with sort_keys=True.
# =============================================================================
def dumps_sorted_with_json():
    json.dumps(test_object, sort_keys=True)


def dumps_sorted_with_yajl():
    yajl.dumps(test_object, sort_keys=True)


def dumps_sorted_with_hyperjson():
    hyperjson.dumps(test_object, sort_keys=True)


def dumps_sorted_with_simplejson():
    simplejson.dumps(test_object, sort_keys=True)


def dumps_sorted_with_ujson():
    ujson.dumps(test_object, ensure_ascii=False, sort_keys=True)


# =============================================================================
# JSON decoding.
# =============================================================================
def loads_with_hyperjson():
    hyperjson.loads(decode_data)


def loads_with_json():
    json.loads(decode_data)


def loads_with_simplejson():
    simplejson.loads(decode_data)


def loads_with_ujson():
    ujson.loads(decode_data)


def loads_with_yajl():
    yajl.loads(decode_data)


# =============================================================================
# Benchmarks.
# =============================================================================
def run_decode(count):
    results_record_result(loads_with_hyperjson, False, count)
    if not skip_lib_comparisons:
        results_record_result(loads_with_ujson, False, count)
        results_record_result(loads_with_simplejson, False, count)
        results_record_result(loads_with_yajl, False, count)
        results_record_result(loads_with_json, False, count)


def run_encode(count):
    results_record_result(dumps_with_hyperjson, True, count)
    if not skip_lib_comparisons:
        results_record_result(dumps_with_ujson, True, count)
        results_record_result(dumps_with_simplejson, True, count)
        results_record_result(dumps_with_yajl, True, count)
        results_record_result(dumps_with_json, True, count)


def run_encode_sort_keys(count):
    results_record_result(dumps_sorted_with_hyperjson, True, count)
    if not skip_lib_comparisons:
        results_record_result(dumps_sorted_with_ujson, True, count)
        results_record_result(dumps_sorted_with_simplejson, True, count)
        results_record_result(dumps_sorted_with_yajl, True, count)
        results_record_result(dumps_sorted_with_json, True, count)


def benchmark_array_doubles():
    global decode_data, test_object
    results_new_benchmark("Array with 256 doubles")
    COUNT = 10000

    test_object = [sys.maxsize * random.random() for _ in range(256)]

    run_encode(COUNT)

    decode_data = json.dumps(test_object)
    test_object = None
    run_decode(COUNT)

    decode_data = None


def benchmark_array_utf8_strings():
    global decode_data, test_object
    results_new_benchmark("Array with 256 UTF-8 strings")
    COUNT = 2000

    s = "نظام الحكم سلطاني وراثي في الذكور من ذرية السيد تركي بن سعيد بن سلطان ويشترط فيمن يختار لولاية الحكم من بينهم ان يكون مسلما رشيدا عاقلا ًوابنا شرعيا لابوين عمانيين "
    test_object = [s] * 256
    run_encode(COUNT)

    decode_data = json.dumps(test_object)
    test_object = None
    run_decode(COUNT)

    decode_data = None


def benchmark_array_byte_strings():
    global decode_data, test_object
    results_new_benchmark("Array with 256 strings")
    COUNT = 10000

    test_object = ["A pretty long string which is in a list"] * 256
    run_encode(COUNT)

    decode_data = json.dumps(test_object)
    test_object = None
    run_decode(COUNT)

    decode_data = None


def benchmark_medium_complex_object():
    global decode_data, test_object
    results_new_benchmark("Medium complex object")
    COUNT = 5000

    test_object = [[USER, FRIENDS], [USER, FRIENDS], [USER, FRIENDS], [
        USER, FRIENDS], [USER, FRIENDS], [USER, FRIENDS]]
    run_encode(COUNT)

    decode_data = json.dumps(test_object)
    test_object = None
    run_decode(COUNT)

    decode_data = None


def benchmark_array_true_values():
    global decode_data, test_object
    results_new_benchmark("Array with 256 True values")
    COUNT = 50000

    test_object = [True] * 256
    run_encode(COUNT)

    decode_data = json.dumps(test_object)
    test_object = None
    run_decode(COUNT)

    decode_data = None


def benchmark_array_of_dict_string_int_pairs():
    global decode_data, test_object
    results_new_benchmark("Array with 256 dict{string, int} pairs")
    COUNT = 5000

    test_object = []
    for x in range(256):
        test_object.append(
            {str(random.random()*20): int(random.random()*1000000)})
    run_encode(COUNT)

    decode_data = json.dumps(test_object)
    test_object = None
    run_decode(COUNT)

    decode_data = None


def benchmark_dict_of_arrays_of_dict_string_int_pairs():
    global decode_data, test_object
    results_new_benchmark(
        "Dict with 256 arrays with 256 dict{string, int} pairs")
    COUNT = 50

    test_object = {}
    for _ in range(256):
        arrays = [{str(random.random()*20): int(random.random()*1000000)}
                  for _ in range(256)]
        test_object[str(random.random()*20)] = arrays
    run_encode(COUNT)

    decode_data = json.dumps(test_object)
    run_decode(COUNT)

    decode_data = None

    results_new_benchmark(
        "Dict with 256 arrays with 256 dict{string, int} pairs, outputting sorted keys")
    run_encode_sort_keys(COUNT)

    test_object = None


def benchmark_complex_object():
    global decode_data, test_object
    results_new_benchmark("Complex object")
    COUNT = 100

    with open(os.path.join(os.path.dirname(__file__), "sample.json"), "r") as f:
        test_object = json.load(f)
    run_encode(COUNT)

    decode_data = json.dumps(test_object)
    test_object = None
    run_decode(COUNT)

    decode_data = None


# =============================================================================
# Main.
# =============================================================================
if __name__ == "__main__":
    if len(sys.argv) > 1 and "skip-lib-comps" in sys.argv:
        skip_lib_comparisons = True

    benchmark_array_doubles()
    benchmark_array_utf8_strings()
    benchmark_array_byte_strings()
    benchmark_medium_complex_object()
    benchmark_array_true_values()
    benchmark_array_of_dict_string_int_pairs()
    benchmark_dict_of_arrays_of_dict_string_int_pairs()
    # Disabled for now because of https://github.com/PyO3/pyo3/issues/177
    # benchmark_complex_object()
    if not skip_lib_comparisons:
        results_output_table()
