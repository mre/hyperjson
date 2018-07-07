#![feature(proc_macro)]
#![feature(proc_macro_path_invoc)]
#![feature(try_from)]
#![feature(test)]

extern crate test;

extern crate serde;

#[macro_use]
extern crate failure;
#[macro_use]
extern crate serde_derive;

#[macro_use]
extern crate version;

#[macro_use]
extern crate pyo3;
extern crate serde_json;

use std::collections::BTreeMap;
use std::convert::TryFrom;
use std::convert::TryInto;

use failure::Error;
use pyo3::prelude::*;
use pyo3::Python;

struct HyperJsonValue<'a> {
    py: &'a Python<'a>,
    inner: &'a serde_json::Value,
    parse_float: &'a Option<PyObject>,
    parse_int: &'a Option<PyObject>,
}

#[derive(Debug, Fail)]
pub enum HyperJsonError {
    #[fail(display = "Conversion error: {}", error)]
    InvalidConversion { error: serde_json::Error },
    #[fail(display = "Python Runtime exception: {}", error)]
    PyErr { error: String },
    #[fail(display = "Dictionary key is not a string: {:?}", obj)]
    DictKeyNotString { obj: PyObject },
    #[fail(display = "Invalid float: {}", x)]
    InvalidFloat { x: String },
    #[fail(display = "Invalid type: {}, Error: {}", t, e)]
    InvalidCast { t: String, e: String },
    // NoneError doesn't have an impl for `Display`
    // See https://github.com/rust-lang-nursery/failure/issues/61
    // See https://github.com/rust-lang/rust/issues/42327#issuecomment-378324282
    // #[fail(display = "Error: {}", s)]
    // NoneError { s: String },
}

impl From<serde_json::Error> for HyperJsonError {
    fn from(error: serde_json::Error) -> HyperJsonError {
        HyperJsonError::InvalidConversion { error }
    }
}

impl From<HyperJsonError> for pyo3::PyErr {
    fn from(h: HyperJsonError) -> pyo3::PyErr {
        match h {
            HyperJsonError::InvalidConversion { error } => {
                PyErr::new::<pyo3::exc::TypeError, _>(format!("{}", error))
            }
            // TODO
            HyperJsonError::PyErr { error } => PyErr::new::<pyo3::exc::TypeError, _>("PyErr"),
            HyperJsonError::InvalidCast { t, e } => {
                PyErr::new::<pyo3::exc::TypeError, _>("InvalidCast")
            }
            _ => PyErr::new::<pyo3::exc::TypeError, _>("Unknown reason"),
        }
    }
}

impl From<pyo3::PyErr> for HyperJsonError {
    fn from(error: pyo3::PyErr) -> HyperJsonError {
        // TODO: This should probably just have the underlying pyo3::PyErr as an argument,
        // but this type is not `Sync`, so we just use the debug representation for now.
        HyperJsonError::PyErr {
            error: format!("{:?}", error),
        }
    }
}

import_exception!(json, JSONDecodeError);

/// A hyper-fast JSON encoder/decoder written in Rust
#[py::modinit(_hyperjson)]
fn init(py: Python, m: &PyModule) -> PyResult<()> {
    // See https://github.com/PyO3/pyo3/issues/171
    // Use JSONDecodeError from stdlib until issue is resolved.
    // py_exception!(_hyperjson, JSONDecodeError);
    // m.add("JSONDecodeError", py.get_type::<JSONDecodeError>());

    #[pyfn(m, "load")]
    pub fn load_fn(py: Python, fp: PyObject, kwargs: Option<&PyDict>) -> PyResult<PyObject> {
        // Temporary workaround for
        // https://github.com/PyO3/pyo3/issues/145
        let io: &PyObjectRef = fp.as_ref(py);

        // Alternative workaround
        // fp.getattr(py, "seek")?;
        // fp.getattr(py, "read")?;

        // Reset file pointer to beginning See
        // https://github.com/PyO3/pyo3/issues/143 Note that we ignore the return
        // value, because `seek` does not strictly need to exist on the object
        let _success = io.call_method("seek", (0,), pyo3::NoArgs);

        let s_obj = io.call_method0("read")?;
        loads_fn(
            py,
            s_obj.to_object(py),
            None,
            None,
            None,
            None,
            None,
            kwargs,
        )
    }

    m.add("__version__", version!());

    // This function is a poor man's implementation of
    // impl From<&str> for PyResult<PyObject>, which is not possible,
    // because we have none of these types under our control.
    // Note: Encoding param is deprecated and ignored.
    #[pyfn(m, "loads")]
    pub fn loads_fn(
        py: Python,
        s: PyObject,
        encoding: Option<PyObject>,
        cls: Option<PyObject>,
        object_hook: Option<PyObject>,
        parse_float: Option<PyObject>,
        parse_int: Option<PyObject>,
        kwargs: Option<&PyDict>,
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

        // This was moved out of the Python module code to enable benchmarking.
        loads_impl(
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

    #[pyfn(m, "dumps")] // ensure_ascii, check_circular, allow_nan, cls, indent, separators, default, sort_keys, kwargs = "**")]
    pub fn dumps_fn(
        py: Python,
        obj: PyObject,
        skipkeys: Option<bool>,
        ensure_ascii: Option<PyObject>,
        check_circular: Option<PyObject>,
        allow_nan: Option<PyObject>,
        cls: Option<PyObject>,
        indent: Option<PyObject>,
        separators: Option<PyObject>,
        default: Option<PyObject>,
        sort_keys: Option<PyObject>,
        kwargs: Option<&PyDict>,
    ) -> PyResult<PyObject> {
        let v = to_json(py, &obj)?;
        let s: Result<String, HyperJsonError> =
            serde_json::to_string(&v).map_err(|error| HyperJsonError::InvalidConversion { error });
        Ok(s?.to_object(py))
    }

    #[pyfn(m, "dump")]
    pub fn dump_fn(
        py: Python,
        obj: PyObject,
        fp: PyObject,
        skipkeys: Option<PyObject>,
        ensure_ascii: Option<PyObject>,
        check_circular: Option<PyObject>,
        allow_nan: Option<PyObject>,
        cls: Option<PyObject>,
        indent: Option<PyObject>,
        separators: Option<PyObject>,
        default: Option<PyObject>,
        sort_keys: Option<PyObject>,
        kwargs: Option<&PyDict>,
    ) -> PyResult<PyObject> {
        let s = dumps_fn(
            py, obj, None, None, None, None, None, None, None, None, None, None,
        )?;
        let fp_ref: &PyObjectRef = fp.as_ref(py);
        fp_ref.call_method1("write", (s,))?;
        // TODO: Will this always return None?
        Ok(pyo3::Python::None(py))
    }

    Ok(())
}

pub fn loads_impl(
    py: Python,
    s: PyObject,
    encoding: Option<PyObject>,
    cls: Option<PyObject>,
    object_hook: Option<PyObject>,
    parse_float: Option<PyObject>,
    parse_int: Option<PyObject>,
    kwargs: Option<&PyDict>,
) -> PyResult<PyObject> {
    let string_result: Result<&PyString, _> = s.cast_as::<PyString>(py);
    //PyString::from_object(s.as_ref(py), "utf-8", "strict");
    match string_result {
        Ok(string) => {
            let utf8_str = string.to_string_lossy();
            let v = serde_json::from_str(&utf8_str);
            match v {
                Ok(serde_val) => {
                    return HyperJsonValue::new(&py, &serde_val, &parse_float, &parse_int)
                        .try_into();
                }
                Err(e) => {
                    return convert_special_floats(py, &utf8_str, parse_int).or_else(|err| {
                        if e.is_syntax() {
                            return Err(JSONDecodeError::new((
                                format!("Error: {:?}", err),
                                "bla",
                                0,
                            )));
                        } else {
                            return Err(exc::ValueError::new(format!("Error: {:?}", e)));
                        }
                    });
                }
            }
        }
        _ => {
            let bytes: &PyBytes = PyObject::extract(&s, py).or_else(|e| {
                Err(exc::TypeError::new(format!(
                    "the JSON object must be str, bytes or bytearray, got: {:?}",
                    e
                )))
            })?;
            let v = serde_json::from_slice(&bytes.data());
            match v {
                Ok(serde_val) => {
                    return HyperJsonValue::new(&py, &serde_val, &parse_float, &parse_int)
                        .try_into();
                }
                Err(e) => {
                    return Err(exc::TypeError::new(format!(
                        "the JSON object must be str, bytes or bytearray, got: {:?}",
                        e
                    )));
                }
            }
        }
    }
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
                return serde_json::value::to_value(val)
                    .map_err(|error| HyperJsonError::InvalidConversion { error });
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
                Err(HyperJsonError::DictKeyNotString {
                    obj: key_obj.to_object(py),
                })
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
            None => Err(HyperJsonError::InvalidFloat {
                x: format!("{}", x),
            }),
        }
    });
    extract!(u64);
    extract!(i64);

    if obj == &py.None() {
        return Ok(serde_json::Value::Null);
    }

    // At this point we can't cast it, set up the error object
    let repr = obj
        .as_ref(py)
        .repr()
        .and_then(|x| x.to_string().and_then(|y| Ok(y.into_owned())));
    Err(HyperJsonError::InvalidCast {
        t: obj.as_ref(py).get_type().name().into_owned(),
        e: repr?,
    })
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

impl<'a> TryFrom<HyperJsonValue<'a>> for PyObject {
    type Error = PyErr;
    fn try_from(v: HyperJsonValue) -> Result<PyObject, PyErr> {
        match v.inner {
            serde_json::Value::Number(ref x) => {
                if x.is_u64() {
                    // TODO: Do we need to use the use parse_int here as below?
                    let u_int = x.as_u64().ok_or_else(|| HyperJsonError::InvalidCast {
                        t: x.to_string(),
                        e: "Cannot convert to u64".to_string(),
                    })?;
                    match v.parse_int {
                        Some(parser) => Ok(parser.call1(*v.py, (u_int,))?),
                        None => Ok(u_int.to_object(*v.py)),
                    }
                } else if x.is_i64() {
                    let u_int = x.as_i64().ok_or_else(|| HyperJsonError::InvalidCast {
                        t: x.to_string(),
                        e: "Cannot convert to i64".to_string(),
                    })?;
                    match v.parse_int {
                        Some(parser) => Ok(parser.call1(*v.py, (u_int,))?),
                        None => Ok(u_int.to_object(*v.py)),
                    }
                } else {
                    let f = x.as_f64().ok_or_else(|| HyperJsonError::InvalidCast {
                        t: x.to_string(),
                        e: "Cannot convert to f64".to_string(),
                    })?;
                    match v.parse_float {
                        Some(parser) => Ok(parser.call1(*v.py, (f,))?),
                        None => Ok(f.to_object(*v.py)),
                    }
                }
            }
            serde_json::Value::String(ref x) => Ok(x.to_object(*v.py)),
            serde_json::Value::Null => Ok(v.py.None()),
            serde_json::Value::Bool(ref b) => Ok(b.to_object(*v.py)),
            serde_json::Value::Array(ref a) => {
                let ret: Result<Vec<PyObject>, _> = a
                    .iter()
                    .map(|elem| {
                        HyperJsonValue::new(v.py, elem, &v.parse_float, &v.parse_int).try_into()
                    })
                    .collect();
                Ok(ret?.to_object(*v.py))
            }
            serde_json::Value::Object(ref o) => {
                let ret: Result<BTreeMap<String, PyObject>, _> = o
                    .iter()
                    .map(|(k, x)| {
                        let key = k.to_string();
                        let value =
                            HyperJsonValue::new(v.py, x, v.parse_float, v.parse_int).try_into();
                        match value {
                            Ok(val) => Ok((key, val)),
                            Err(e) => Err(e),
                        }
                    })
                    .collect();
                Ok(ret?.to_object(*v.py))
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::io::Read;
    use test::Bencher;

    #[bench]
    fn bench_dict_string_int_pairs(b: &mut Bencher) {
        let mut f = File::open("benchmark/dict_string_int_plain.txt").unwrap();
        let mut dict_string_int = String::new();
        f.read_to_string(&mut dict_string_int).unwrap();

        let gil = Python::acquire_gil();
        let py = gil.python();

        b.iter(|| {
            let obj = dict_string_int.to_object(py);
            loads_impl(py, obj, None, None, None, None, None, None)
        });
    }
}
