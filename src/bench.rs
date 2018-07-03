//! Simple benchmark for finding hotspots using profilers like callgrind.
//! Usage:
//!
//! ```
//! Cargo build
//! valgrind --tool=callgrind --main-stacksize=1000000000 target/debug/hyperjson-bench
//! callgrind_annotate --auto=yes callgrind.out.35583 >out.rs
//! qcachegrind callgrind.out.35583
//! ```
extern crate hyperjson;
extern crate pyo3;

use pyo3::prelude::*;
use pyo3::Python;
use std::fs::File;
use std::io::Read;

fn main() {
    let mut f = File::open("benchmark/dict_string_int_plain.txt").unwrap();
    let mut dict_string_int = String::new();
    f.read_to_string(&mut dict_string_int).unwrap();

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
