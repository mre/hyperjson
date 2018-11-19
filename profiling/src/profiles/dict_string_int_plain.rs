use pyo3::prelude::*;
use std::fs;

pub fn exec(iterations: u64) {
    let bench_file_name = "benchmarks/dict_string_int_plain.txt";

    let dict_string_int = fs::read_to_string(bench_file_name)
        .expect(&format!("Could not open bench file '{}'", bench_file_name));

    let gil = Python::acquire_gil();
    let py = gil.python();

    let obj = dict_string_int.to_object(py);

    for _ in 0..iterations {
        println!(
            "{}",
            hyperjson::loads_impl(py, obj.clone_ref(py), None, None, None, None, None, None)
                .is_ok()
        );
    }
}
