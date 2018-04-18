# hyperjson

A Python module to load json data.
It's a thin wrapper around Rust's [serde-json](https://github.com/serde-rs/json) built with [pyo3](https://github.com/PyO3/pyo3).

## Motivation

Parsing JSON is a solved problem.  
There are literally a thousand libraries out there to read and write JSON.  
So, no need to reinvent the wheel, right?  
Except, maybe there is: performance and safety.

Only if you handle a lot of JSON, you might see a performance impact.
But due to Rust, the risk of running into stack overflows or segmentation faults is lower --
especially in comparison with C extensions to parse JSON.

## TODO (help wanted!)

- [X] loads()
- [ ] load()
- [ ] dumps()
- [ ] dump()
- [ ] Benchmark against json and ujson

## References

* [ultrajson bugs containing segmentation faults and overflows](https://github.com/esnme/ultrajson/issues)
* [Benchmark data](https://users.rust-lang.org/t/serde-and-serde-json-1-0-0-released/10466/3)
* [Comments on benchmark data](https://www.reddit.com/r/rust/comments/6albr0/serde_compared_to_the_fastest_c_json_library/)
* [Another benchmark](https://github.com/serde-rs/json-benchmark)
* [Some ultrajson benchmarks](https://pypi.python.org/pypi/ujson)