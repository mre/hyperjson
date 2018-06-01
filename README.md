![hyperjson](logo.gif)

A hyper-fast, safe Python module to read and write JSON data. Works as a
drop-in replacement for Python's built-in
[json](https://docs.python.org/3/library/json.html) module. It's a thin wrapper
around Rust's [serde-json](https://github.com/serde-rs/json) built with
[pyo3](https://github.com/PyO3/pyo3). Compatible with Python 3. Should also work
on Python 2, but it's not officially supported.

## Usage

hyperjson is meant as a drop-in replacement for Python's [json
module](https://docs.python.org/3/library/json.html):  

```python
>>> import hyperjson 
>>> hyperjson.dumps([{"key": "value"}, 81, True])
'[{"key":"value"},81,true]'
>>> hyperjson.loads("""[{"key": "value"}, 81, true]""")
[{u'key': u'value'}, 81, True
```

## Motivation

Parsing JSON is a solved problem. So, no need to reinvent the wheel, right?  
Unless you care about **performance and safety**.

Turns out, parsing JSON correctly is [hard](http://seriot.ch/parsing_json.php), but due to Rust, the risk of running
into [stack overflows or segmentation faults](https://github.com/esnme/ultrajson/issues) is lower (basically zero, especially in comparison to C implementations).

## Goals

* **Compatibility**: Support the full feature-set of Python's json module.
* **Safety**: No segfaults, panics, or overflows.
* **Performance**: Significantly faster than json and as fast as ujson (both written in C).

## Non-goals

* **Support ujson and simplejson extensions**:  
  Custom extensions like `encode()`, `__json__()`, or `toDict()` are not supported.
  The reason is, that they go against PEP8 (e.g. `dunder` functions are restricted to the standard
  library, camelCase is not pythonic) and are not available in Python's json
  module.

## Installation

To compile the code and create an importable Python module from it, call  

```
make install
```

From there, you can simply use it from Python as seen in the usage example above.

## Contributions welcome!

If you like to hack on hyperjson, here is what needs to be done:

- [X] Implement [`loads()`](https://docs.python.org/3/library/json.html#json.loads)
- [X] Implement [`load()`](https://docs.python.org/3/library/json.html#json.load)
- [X] Implement [`dumps()`](https://docs.python.org/3/library/json.html#json.dumps)
- [X] Implement [`dump()`](https://docs.python.org/3/library/json.html#json.dump)
- [ ] Benchmark against [json](https://docs.python.org/3/library/json.html) and
  [ujson](https://github.com/esnme/ultrajson/) (see [#1](https://github.com/mre/hyperjson/issues/1))
- [ ] Add remaining [keyword-only arguments](https://docs.python.org/3/library/json.html#basic-usage) to methods
- [ ] Create a proper pip package from it to make installing easier (see [#3](https://github.com/mre/hyperjson/issues/3)).
- [ ] Add a CI/CD pipeline for easier testing (see [#2](https://github.com/mre/hyperjson/issues/2))

## Developer guide

To get started, first you need to get [setuptools-rust](https://github.com/PyO3/setuptools-rust):

```
git clone git@github.com:PyO3/setuptools-rust.git
cd setuptools-rust
python setup.py install
```

After that, you can install hyperjson from the project's root folder:

```
cd /path/to/hyperjson
make install
```

To test your changes, run

```
make test
```

## License

hyperjson is licensed under either of

* Apache License, Version 2.0, (LICENSE-APACHE or
  http://www.apache.org/licenses/LICENSE-2.0)
* MIT license (LICENSE-MIT or http://opensource.org/licenses/MIT)

at your option.

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted
for inclusion in hyperjson by you, as defined in the Apache-2.0 license, shall
be dual licensed as above, without any additional terms or conditions.
