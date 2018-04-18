#![feature(proc_macro)]

extern crate pyo3;
extern crate serde_json;

use pyo3::prelude::*;
use pyo3::Python;
use std::collections::BTreeMap;

enum HyperJsonError {
    SerdeError,
}

impl From<serde_json::Error> for HyperJsonError {
    fn from(_s: serde_json::Error) -> HyperJsonError {
        HyperJsonError::SerdeError
    }
}

impl From<HyperJsonError> for pyo3::PyErr {
    fn from(_h: HyperJsonError) -> pyo3::PyErr {
        PyErr::new::<pyo3::exc::TypeError, _>("Error message")
    }
}

/// Module documentation string
#[py::modinit(_hyperjson)]
fn init(py: Python, m: &PyModule) -> PyResult<()> {
    #[pyfn(m, "loads", s, encoding, kwargs = "**")]
    fn loads_fn(
        py: Python,
        s: String,
        encoding: Option<String>,
        kwargs: Option<&PyDict>,
    ) -> PyResult<PyObject> {
        loads(py, s, encoding, kwargs)
    }
    Ok(())
}

fn loads(
    py: Python,
    s: String,
    encoding: Option<String>,
    kwargs: Option<&PyDict>,
) -> PyResult<PyObject> {
    // if let Some(kwargs) = kwargs {
    //     for (key, val) in kwargs.iter() {
    //         println!("{} = {}", key, val);
    //     }
    // }

    if let Some(encoding) = encoding {
        return Err(exc::LookupError::new(format!(
            "Unknown encoding: {}",
            encoding
        )));
    }

    // if args.len() == 0 {
    //     // TODO: This is the wrong error message.
    //     return Err(exc::LookupError::new("oh no"));
    // }
    // if args.len() >= 2 {
    //     // return Err(exc::TypeError::new(format!(
    //     //     "Unknown encoding: {}",
    //     //     args.get_item(1).to_string()
    //     // )));
    //     return Err(exc::LookupError::new(
    //         "loads() takes exactly 1 argument (2 given)",
    //     ));
    // }
    // let s = args.get_item(0).to_string();
    convert_string(py, s)
}

fn convert_string(py: Python, s: String) -> PyResult<PyObject> {
    let v = serde_json::from_str(&s);
    match v {
        Ok(serde_val) => convert(py, &serde_val),
        Err(e) => match s.as_ref() {
            // TODO: If `allow_nan` is false (default: True), then this should be a ValueError
            // https://docs.python.org/3/library/json.html
            "NaN" => Ok(std::f64::NAN.to_object(py)),
            "Infinity" => Ok(std::f64::INFINITY.to_object(py)),
            "-Infinity" => Ok(std::f64::NEG_INFINITY.to_object(py)),
            _ => Err(exc::ValueError::new(format!(
                "Value: {:?}, Error: {}",
                s, e
            ))),
        },
    }
}

fn convert(py: Python, v: &serde_json::Value) -> PyResult<PyObject> {
    match v {
        serde_json::Value::Number(ref v) => {
            if v.is_i64() {
                Ok(PyInt::new(py, v.as_i64().unwrap()).to_object(py))
            } else {
                Ok(PyFloat::new(py, v.as_f64().unwrap()).to_object(py))
            }
        }
        serde_json::Value::String(ref v) => Ok(v.to_object(py)),
        serde_json::Value::Null => Ok(py.None()),
        serde_json::Value::Bool(ref b) => Ok(b.to_object(py)),
        serde_json::Value::Array(ref a) => {
            let mut ar = vec![];

            for elem in a {
                ar.push(convert(py, elem)?);
            }
            Ok(ar.to_object(py))
        }
        serde_json::Value::Object(ref o) => {
            let mut m: BTreeMap<String, pyo3::PyObject> = BTreeMap::new();
            for (k, v) in o.iter() {
                m.insert(k.to_string(), convert(py, v)?);
            }
            Ok(m.to_object(py))
        }
    }
}
