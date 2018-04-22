#![feature(proc_macro)]

extern crate pyo3;
extern crate serde_json;

use pyo3::PyTryFrom;
use pyo3::Python;
use pyo3::prelude::*;
use std::collections::BTreeMap;

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
        s: String,
        encoding: Option<String>,
        kwargs: Option<&PyDict>,
    ) -> PyResult<PyObject> {
        loads(py, s, encoding, kwargs)
    }
    Ok(())
}

fn load(py: Python, fp: PyObject, kwargs: Option<&PyDict>) -> PyResult<PyObject> {
    // let s_bool = fp.call_method0(py, "readable")?;
    // println!("Readable? {:?}", s_bool.as_ref(py));
    // let s_obj = fp.call_method0(py, "read")?;
    // println!("Result after read: {:?}", s_obj);
    // let s = s_obj.as_ref(py);
    // println!("Result after as_ref {:?}", s);

    // let s_obj = fp.call_method0(py, "read")?;
    // let s: String = pyo3::PyString::from(s_obj);
    // println!("{:?}", s);

    fp.call_method(py, "seek", (0,), NoArgs)?;
    let s_obj = fp.call_method0(py, "read")?;
    let s: Result<String, _> = s_obj.extract(py);
    // let s_obj = fp.getattr(py, "read")?;
    // println!("huh? {:?}", s_obj);
    // let s: String = s_obj.extract(py)?;
    // println!("More {:?}", s);

    // let func = fp.getattr(py, "read")?;
    // func.call(py, (-1,), NoArgs)

    // Ok(1.to_object(py))

    //let pystr: Result<PyBytes, _> = s.extract(py);
    // let pystr: Result<&PyString, _> = pyo3::PyTryFrom::try_from(&s_obj.as_ref(py));
    // println!("{:?}", pystr);
    match s {
        Ok(something) => loads(py, something, None, kwargs),
        _ => Err(exc::TypeError::new(format!(
            "string or none type is required as host, got: {:?}",
            s
        ))),
    }
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
                Ok(v.as_i64().unwrap().to_object(py))
            } else {
                Ok(v.as_f64().unwrap().to_object(py))
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
