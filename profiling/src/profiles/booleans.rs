use pyo3::prelude::*;

pub fn exec(iterations: u64) {
    let gil = Python::acquire_gil();
    let py = gil.python();

    let booleans = format!("[{} \"true\"]", "\"true\",".repeat(255));
    let obj = booleans.to_object(py);

    for _ in 0..iterations {
        let deserialized =
            hyperjson::loads_impl(py, obj.clone_ref(py), None, None, None, None, None, None)
                .unwrap();
        println!(
            "{}",
            hyperjson::dumps(
                py,
                deserialized,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ).is_ok()
        );
    }
}
