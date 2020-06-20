use failure::Fail;
use pyo3::{exceptions::TypeError as PyTypeError, import_exception, PyErr, PyObject};

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
    #[fail(display = "Utf8 error: {}", error)]
    Utf8Error { error: std::string::FromUtf8Error },
}

impl From<serde_json::Error> for HyperJsonError {
    fn from(error: serde_json::Error) -> HyperJsonError {
        HyperJsonError::InvalidConversion { error }
    }
}

impl From<HyperJsonError> for PyErr {
    fn from(h: HyperJsonError) -> PyErr {
        match h {
            HyperJsonError::InvalidConversion { error } => {
                PyErr::new::<PyTypeError, _>(format!("{}", error))
            }
            // TODO
            HyperJsonError::PyErr { error: _error } => PyErr::new::<PyTypeError, _>("PyErr"),
            HyperJsonError::InvalidCast { t: _t, e: _e } => {
                PyErr::new::<PyTypeError, _>("InvalidCast")
            }
            _ => PyErr::new::<PyTypeError, _>("Unknown reason"),
        }
    }
}

impl From<PyErr> for HyperJsonError {
    fn from(error: PyErr) -> HyperJsonError {
        // TODO: This should probably just have the underlying PyErr as an argument,
        // but this type is not `Sync`, so we just use the debug representation for now.
        HyperJsonError::PyErr {
            error: format!("{:?}", error),
        }
    }
}

import_exception!(json, JSONDecodeError);
