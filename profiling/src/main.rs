//! Simple benchmark for finding hotspots using profilers like callgrind.
//! Usage:
//!
//! ```
//! cargo build
//! valgrind --tool=callgrind --main-stacksize=1000000000 target/debug/hyperjson-bench
//! callgrind_annotate --auto=yes callgrind.out.35583 >out.rs
//! qcachegrind callgrind.out.35583
//! ```
extern crate hyperjson;
extern crate pyo3;

use pyo3::prelude::*;
use std::fs;

fn main() {
    let bench_file_name = "benchmarks/dict_string_int_plain.txt";

    let dict_string_int = fs::read_to_string(bench_file_name)
        .expect(&format!("Could not open bench file '{}'", bench_file_name));

    let gil = Python::acquire_gil();
    let py = gil.python();

    for _ in 1..10 {
        let obj = dict_string_int.to_object(py);
        println!(
            "{}",
            hyperjson::loads_impl(py, obj, None, None, None, None, None, None).is_ok()
        );
    }
}

