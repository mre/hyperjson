#![feature(proc_macro)]

extern crate pyo3;
extern crate serde_json;

use pyo3::Python;
use pyo3::prelude::*;
use std::collections::BTreeMap;

struct HyperJsonValue<'a> {
    py: &'a Python<'a>,
    inner: &'a serde_json::Value,
    parse_float: &'a Option<PyObject>,
    parse_int: &'a Option<PyObject>,
}

pub enum HyperJsonError {
    SerdeError(serde_json::Error),
    PyErr(PyErr),
    DictKeyNotString(PyObject),
    InvalidFloat,
    TypeError(String, PyResult<String>),
    FixMeTypeError,
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

impl From<pyo3::PyErr> for HyperJsonError {
    fn from(p: pyo3::PyErr) -> HyperJsonError {
        HyperJsonError::PyErr(p)
    }
}

/// Module documentation string
#[py::modinit(_hyperjson)]
fn init(py: Python, m: &PyModule) -> PyResult<()> {
    #[pyfn(m, "load", fp, kwargs = "**")]
    fn load_fn(py: Python, fp: PyObject, kwargs: Option<&PyDict>) -> PyResult<PyObject> {
        load(py, fp, kwargs)
    }

    #[pyfn(m, "loads", s, "*", encoding, cls, object_hook, parse_float, parse_int, parse_constant,
           object_hook, kwargs = "**")]
    fn loads_fn(
        py: Python,
        s: &str,
        encoding: Option<PyObject>,
        cls: Option<PyObject>,
        object_hook: Option<PyObject>,
        parse_float: Option<PyObject>,
        parse_int: Option<PyObject>,
        kwargs: Option<&PyDict>,
    ) -> PyResult<PyObject> {
        loads(
            py,
            s,
            encoding,
            cls,
            object_hook,
            parse_float,
            parse_int,
            kwargs,
        )
    }

    #[pyfn(m, "dumps", obj)]
    fn dumps_fn(
        py: Python,
        obj: PyObject,
        //  skipkeys: Option<PyObject>,
        //         ensure_ascii: Option<PyObject>,
        //         check_circular: Option<PyObject>, allow_nan: Option<PyObject>,
        //         cls: Option<PyObject>, indent: Option<PyObject>,
        //         separators: Option<PyObject>, default: Option<PyObject>,
        //         sort_keys: Option<PyObject>, kwargs: Option<&PyDict>
    ) -> PyResult<PyObject> {
        let v = to_json(py, &obj)?;
        let s: Result<String, HyperJsonError> =
            serde_json::to_string(&v).map_err(|e| HyperJsonError::SerdeError(e));
        Ok(s?.to_object(py))
    }

    #[pyfn(m, "dump", obj, fp)]
    fn dump_fn(
        py: Python,
        obj: PyObject,
        fp: PyObject,
        //  skipkeys: Option<PyObject>,
        //         ensure_ascii: Option<PyObject>,
        //         check_circular: Option<PyObject>, allow_nan: Option<PyObject>,
        //         cls: Option<PyObject>, indent: Option<PyObject>,
        //         separators: Option<PyObject>, default: Option<PyObject>,
        //         sort_keys: Option<PyObject>, kwargs: Option<&PyDict>
    ) -> PyResult<PyObject> {
        let s = dumps_fn(py, obj)?;
        let fp_ref: &PyObjectRef = fp.as_ref(py);
        fp_ref.call_method1("write", (s,))?;
        // TODO: Will this always return None?
        Ok(pyo3::Python::None(py))
        // let result: Result<String, _> = s_obj.extract(py);
        // match result {
        //     Ok(s) => loads(py, &s, None, None, None, None, None, kwargs),
        //     _ => Err(exc::TypeError::new(format!(
        //         "string or none type is required as host, got: {:?}",
        //         result
        //     ))),
        // }
    }

    Ok(())
}

/// Convert from a `cpython::PyObject` to a `serde_json::Value`.
pub fn to_json(py: Python, obj: &PyObject) -> Result<serde_json::Value, HyperJsonError> {
    macro_rules! cast {
        ($t:ty, $f:expr) => {
            if let Ok(val) = obj.cast_as::<$t>(py) {
                return $f(val);
            }
        };
    }

    macro_rules! extract {
        ($t:ty) => {
            if let Ok(val) = obj.extract::<$t>(py) {
                return serde_json::value::to_value(val).map_err(HyperJsonError::SerdeError);
            }
        };
    }

    cast!(PyDict, |x: &PyDict| {
        let mut map = serde_json::Map::new();
        for (key_obj, value) in x.iter() {
            let key = if key_obj == py.None().as_ref(py) {
                Ok("null".to_string())
            } else if let Ok(val) = key_obj.extract::<bool>() {
                Ok(if val {
                    "true".to_string()
                } else {
                    "false".to_string()
                })
            } else if let Ok(val) = key_obj.str() {
                Ok(val.to_string()?.into_owned())
            } else {
                Err(HyperJsonError::DictKeyNotString(key_obj.to_object(py)))
            };
            map.insert(key?, to_json(py, &value.to_object(py))?);
        }
        Ok(serde_json::Value::Object(map))
    });

    cast!(PyList, |x: &PyList| Ok(serde_json::Value::Array(try!(
        x.iter().map(|x| to_json(py, &x.to_object(py))).collect()
    ))));
    cast!(PyTuple, |x: &PyTuple| Ok(serde_json::Value::Array(try!(
        x.iter().map(|x| to_json(py, &x.to_object(py))).collect()
    ))));

    extract!(String);
    extract!(bool);

    cast!(PyFloat, |x: &PyFloat| {
        match serde_json::Number::from_f64(x.value()) {
            Some(n) => Ok(serde_json::Value::Number(n)),
            None => Err(HyperJsonError::InvalidFloat),
        }
    });

    extract!(u64);
    extract!(i64);

    if obj == &py.None() {
        return Ok(serde_json::Value::Null);
    }

    // At this point we can't cast it, set up the error object
    // let repr = obj.repr(py)
    //     .and_then(|x| x.to_string(py).and_then(|y| Ok(y.into_owned())));
    // Err(HyperJsonError::TypeError(
    //     obj.get_type(py).name(py).into_owned(),
    //     repr,
    // ))
    Err(HyperJsonError::FixMeTypeError)
}

fn load(py: Python, fp: PyObject, kwargs: Option<&PyDict>) -> PyResult<PyObject> {
    // Temporary workaround for
    // https://github.com/PyO3/pyo3/issues/145
    let io: &PyObjectRef = fp.as_ref(py);

    // Alternative workaround
    // fp.getattr(py, "seek")?;
    // fp.getattr(py, "read")?;

    // Reset file pointer to beginning
    // See https://github.com/PyO3/pyo3/issues/143
    io.call_method("seek", (0,), pyo3::NoArgs)?;

    let s_obj = io.call_method0("read")?;
    let result: Result<String, _> = s_obj.extract();
    match result {
        Ok(s) => loads(py, &s, None, None, None, None, None, kwargs),
        _ => Err(exc::TypeError::new(format!(
            "string or none type is required as host, got: {:?}",
            result
        ))),
    }
}

// This function is a poor man's implementation of
// impl From<&str> for PyResult<PyObject>, which is not possible,
// because we have none of these types under our control.
// Note: Encoding param is deprecated and ignored.
fn loads(
    py: Python,
    s: &str,
    _encoding: Option<PyObject>,
    _cls: Option<PyObject>,
    _object_hook: Option<PyObject>,
    parse_float: Option<PyObject>,
    parse_int: Option<PyObject>,
    _kwargs: Option<&PyDict>,
) -> PyResult<PyObject> {
    // if let Some(kwargs) = kwargs {
    //     for (key, val) in kwargs.iter() {
    //         println!("{} = {}", key, val);
    //     }
    // }

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
        Ok(serde_val) => HyperJsonValue::new(&py, &serde_val, &parse_float, &parse_int).try_into(),
        Err(e) => convert_special_floats(py, s, parse_int).or(Err(exc::ValueError::new(format!(
            "Value: {:?}, Error: {}",
            s, e
        )))),
    }
}

fn convert_special_floats(py: Python, s: &str, parse_int: Option<PyObject>) -> PyResult<PyObject> {
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
    fn new(
        py: &'a Python,
        inner: &'a serde_json::Value,
        parse_float: &'a Option<PyObject>,
        parse_int: &'a Option<PyObject>,
    ) -> HyperJsonValue<'a> {
        // We cannot borrow the runtime here,
        // because it wouldn't live long enough
        // let gil = Python::acquire_gil();
        // let py = gil.python();
        HyperJsonValue {
            py,
            inner,
            parse_float,
            parse_int,
        }
    }
}

// impl<'a> From<String> for HyperJsonValue<'a> {
//     fn from(v: String) -> HyperJsonValue<'a> {
//                 let gil = Python::acquire_gil();
// let py = gil.python();
//     }
// }
// impl<'a> TryFrom<PyObject> for HyperJsonValue<'a> {
//     type Error = HyperJsonError;
//     fn try_from(p: PyObject) -> Result<HyperJsonValue<'a>, HyperJsonError> {
//         HyperJsonValue::new(p.);
//     }
// }

impl<'a> TryFrom<HyperJsonValue<'a>> for PyObject {
    type Error = PyErr;
    fn try_from(v: HyperJsonValue) -> Result<PyObject, PyErr> {
        match v.inner {
            serde_json::Value::Number(ref x) => {
                // Unwrap should be safe here, since we checked for the correct
                // type before
                if x.is_i64() {
                    match v.parse_int {
                        Some(parser) => {
                            let i = x.as_i64().unwrap();
                            Ok(parser.call1(*v.py, (i,))?)
                        }
                        None => Ok(x.as_i64().unwrap().to_object(*v.py)),
                    }
                } else {
                    match v.parse_float {
                        Some(parser) => {
                            let f = x.as_f64().unwrap();
                            Ok(parser.call1(*v.py, (f,))?)
                        }
                        None => Ok(x.as_f64().unwrap().to_object(*v.py)),
                    }
                }
            }
            serde_json::Value::String(ref x) => Ok(x.to_object(*v.py)),
            serde_json::Value::Null => Ok(v.py.None()),
            serde_json::Value::Bool(ref b) => Ok(b.to_object(*v.py)),
            serde_json::Value::Array(ref a) => {
                let mut ar: Vec<PyObject> = vec![];

                for elem in a {
                    ar.push(
                        HyperJsonValue::new(v.py, elem, &v.parse_float, &v.parse_int).try_into()?,
                    );
                }
                Ok(ar.to_object(*v.py))
            }
            serde_json::Value::Object(ref o) => {
                let mut m: BTreeMap<String, pyo3::PyObject> = BTreeMap::new();
                for (k, x) in o.iter() {
                    m.insert(
                        k.to_string(),
                        HyperJsonValue::new(v.py, x, v.parse_float, v.parse_int).try_into()?,
                    );
                }
                Ok(m.to_object(*v.py))
            }
        }
    }
}
