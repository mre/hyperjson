# hyperjson

A Python module to load JSON data.
It's a thin wrapper around Rust's [serde-json](https://github.com/serde-rs/json) built with [pyo3](https://github.com/PyO3/pyo3).

## Usage

hyperjson is meant to be a drop-in replacement for Python's [json module](https://docs.python.org/3/library/json.html):  

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

Actually, parsing JSON correctly is [quite hard](http://seriot.ch/parsing_json.php),
but due to Rust, the risk of running into stack overflows or segmentation faults is lower (basically non-existent) -- especially in comparison with C implementations.


## TODO (help wanted!)

- [X] [`loads()`](https://docs.python.org/3/library/json.html#json.loads)
- [X] [`load()`](https://docs.python.org/3/library/json.html#json.load)
- [X] [`dumps()`](https://docs.python.org/3/library/json.html#json.dumps)
- [X] [`dump()`](https://docs.python.org/3/library/json.html#json.dump)
- [ ] Benchmark against [json](https://docs.python.org/3/library/json.html) and [ujson](https://github.com/esnme/ultrajson/)
- [ ] Add special flags for methods

## Contributions welcome!

If you want to hack on hyperjson, first install [setuptools-rust](https://github.com/PyO3/setuptools-rust):

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

## References

* [ultrajson bugs containing segmentation faults and overflows](https://github.com/esnme/ultrajson/issues)
* [Benchmark data](https://users.rust-lang.org/t/serde-and-serde-json-1-0-0-released/10466/3)
* [Comments on benchmark data](https://www.reddit.com/r/rust/comments/6albr0/serde_compared_to_the_fastest_c_json_library/)
* [Another benchmark](https://github.com/serde-rs/json-benchmark)
* [Some ultrajson benchmarks](https://pypi.python.org/pypi/ujson)

## License

hyperjson is licensed under either of

* Apache License, Version 2.0, (LICENSE-APACHE or http://www.apache.org/licenses/LICENSE-2.0)
* MIT license (LICENSE-MIT or http://opensource.org/licenses/MIT)

at your option.

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in  
hyperjson by you, as defined in the Apache-2.0 license, shall be dual licensed as above,  
without any additional terms or conditions.