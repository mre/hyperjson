#![feature(proc_macro)]

extern crate pyo3;
extern crate serde_json;

use pyo3::Python;
use pyo3::prelude::*;
use std::collections::BTreeMap;

struct HyperJsonValue<'a> {
    py: &'a Python<'a>,
    inner: &'a serde_json::Value,
}

enum HyperJsonError {
    SerdeError(serde_json::Error),
}

impl From<serde_json::Error> for HyperJsonError {
    fn from(e: serde_json::Error) -> HyperJsonError {
        HyperJsonError::SerdeError(e)
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
    #[pyfn(m, "load", fp, kwargs = "**")]
    fn load_fn(py: Python, fp: PyObject, kwargs: Option<&PyDict>) -> PyResult<PyObject> {
        load(py, fp, kwargs)
    }

    #[pyfn(m, "loads", s, encoding, kwargs = "**")]
    fn loads_fn(
        py: Python,
        s: &str,
        encoding: Option<String>,
        kwargs: Option<&PyDict>,
    ) -> PyResult<PyObject> {
        loads(py, s, encoding, kwargs)
    }
    Ok(())
}

fn load(py: Python, fp: PyObject, kwargs: Option<&PyDict>) -> PyResult<PyObject> {
    // Reset file pointer to beginning
    // See https://github.com/PyO3/pyo3/issues/143
    fp.call_method(py, "seek", (0,), NoArgs)?;

    let s_obj = fp.call_method0(py, "read")?;
    let result: Result<String, _> = s_obj.extract(py);
    match result {
        Ok(s) => loads(py, &s, None, kwargs),
        _ => Err(exc::TypeError::new(format!(
            "string or none type is required as host, got: {:?}", result 
        ))),
    }
}

// This function is a poor man's implementation of 
// impl From<&str> for PyResult<PyObject>, which is not possible,
// because we have none of these types under our control.
fn loads(
    py: Python,
    s: &str,
    encoding: Option<String>,
    _kwargs: Option<&PyDict>,
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

    let v = serde_json::from_str(s);
    match v {
        Ok(serde_val) => PyResult::from(HyperJsonValue::new(&py, &serde_val)),
        Err(e) => convert_number(py, s).or(
            Err(exc::ValueError::new(format!( "Value: {:?}, Error: {}", s, e)))),
    }
}

fn convert_number(py: Python, s: &str) ->PyResult<PyObject> {
    match s {
            // TODO: If `allow_nan` is false (default: True), then this should be a ValueError
            // https://docs.python.org/3/library/json.html
            "NaN" => Ok(std::f64::NAN.to_object(py)),
            "Infinity" => Ok(std::f64::INFINITY.to_object(py)),
            "-Infinity" => Ok(std::f64::NEG_INFINITY.to_object(py)),
            _ => Err(exc::ValueError::new(format!("Value: {:?}", s))),
    }
}

impl<'a> HyperJsonValue<'a> {
    fn new(py: &'a Python, inner: &'a serde_json::Value) -> HyperJsonValue<'a> {
        // We cannot borrow the runtime here,
        // because it wouldn't live long enough
        // let gil = Python::acquire_gil();
        // let py = gil.python();
        HyperJsonValue { py, inner }
    }
}

// impl<'a> From<String> for HyperJsonValue<'a> {
//     fn from(v: String) -> HyperJsonValue<'a> {
//                 let gil = Python::acquire_gil();
// let py = gil.python();
//     }
// }

impl<'a> From<HyperJsonValue<'a>> for PyResult<PyObject> {
    fn from(v: HyperJsonValue) -> PyResult<PyObject> {
        match v.inner {
            serde_json::Value::Number(ref x) => {
                // Unwrap should be safe here, since we checked for the correct
                // type before
                if x.is_i64() {
                    Ok(x.as_i64().unwrap().to_object(*v.py))
                } else {
                    Ok(x.as_f64().unwrap().to_object(*v.py))
                }
            }
            serde_json::Value::String(ref x) => Ok(x.to_object(*v.py)),
            serde_json::Value::Null => Ok(v.py.None()),
            serde_json::Value::Bool(ref b) => Ok(b.to_object(*v.py)),
            serde_json::Value::Array(ref a) => {
                let mut ar = vec![];

                for elem in a {
                    ar.push(PyResult::from(HyperJsonValue::new(v.py, elem))?);
                }
                Ok(ar.to_object(*v.py))
            }
            serde_json::Value::Object(ref o) => {
                let mut m: BTreeMap<String, pyo3::PyObject> = BTreeMap::new();
                for (k, x) in o.iter() {
                    m.insert(k.to_string(), PyResult::from(HyperJsonValue::new(v.py, x))?);
                }
                Ok(m.to_object(*v.py))
            }
        }
    }
}
