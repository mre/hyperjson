![hyperjson](logo.png)

A hyper-fast, native Python module to read and write JSON data. Works as a
drop-in replacement for Python's built-in
[json](https://docs.python.org/3/library/json.html) module. It's a thin wrapper
around Rust's [serde-json](https://github.com/serde-rs/json) built with
[pyo3](https://github.com/PyO3/pyo3). Compatible with Python 3. Should also work
on Python 2, but it's not officially supported.

## Usage

hyperjson is meant to be a drop-in replacement for Python's [json
module](https://docs.python.org/3/library/json.html):  

```python
>>> import hyperjson 
>>> hyperjson.dumps([{"key": "value"}, 81, True])
'[{"key":"value"},81,true]'
>>> hyperjson.loads("""[{"key": "value"}, 81, true]""")
[{u'key': u'value'}, 81, True
```

## Installation

To compile the code and create an importable Python module from it, call  

```
make install
```

## Why?

Parsing JSON is a solved problem.  
There are literally a thousand libraries out there to read and write JSON.  
So, no need to reinvent the wheel, right?  
Except, maybe there is: **performance and safety**.

Turns out, parsing JSON correctly is [quite
hard](http://seriot.ch/parsing_json.php), but due to Rust, the risk of running
into [stack overflows or segmentation faults](https://github.com/esnme/ultrajson/issues) is lower (basically zero, especially in comparison with C implementations).


## TODO (help wanted!)

- [X] [`loads()`](https://docs.python.org/3/library/json.html#json.loads)
- [X] [`load()`](https://docs.python.org/3/library/json.html#json.load)
- [X] [`dumps()`](https://docs.python.org/3/library/json.html#json.dumps)
- [X] [`dump()`](https://docs.python.org/3/library/json.html#json.dump)
- [ ] Benchmark against [json](https://docs.python.org/3/library/json.html) and
  [ujson](https://github.com/esnme/ultrajson/) (see #1)
- [ ] Respect all keyword-only arguments in methods

## Contributions welcome!

If you want to hack on hyperjson, first install
[setuptools-rust](https://github.com/PyO3/setuptools-rust):

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

## Goals

* **Compatibility**: Support the full feature-set of Python's json module
* **Safety**: no segfaults, panics, overflows
* **Performance**: significantly faster than json and as fast as ujson
* **Full compatibility with Python's json module**

## Non-goals

* **Full compatibility with ujson and simplejson**: as such, custom extensions like
  `toDict()`, `__json__()`, or `encode()` are not supported. The reason is, that
  they go against PEP8 (e.g. `dunder` functions are reserved to the standard
  library, camelCase is not pythonic) and are not available in Python's json
  module.

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