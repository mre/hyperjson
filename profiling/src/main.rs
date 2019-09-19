//! Simple hyperjson benchmark for finding hotspots using profilers like perf or callgrind.
//!
//! Example usage on Linux:
//!
//! ```
//! make profile
//! ```
//!
//! Example usage on macOS:
//!
//! ```
//! cargo build --release
//! valgrind --tool=callgrind --main-stacksize=1000000000 target/release/profiling
//! callgrind_annotate --auto=yes callgrind.out.35583 >out.rs
//! qcachegrind callgrind.out.35583
//! ```
extern crate structopt;
#[macro_use]
extern crate clap;

extern crate hyperjson;
extern crate pyo3;

mod profiles;

use structopt::StructOpt;

arg_enum! {
    #[derive(Debug)]
    enum Profile {
        DictStringIntPlain,
        Booleans
    }
}

#[derive(StructOpt, Debug)]
struct Opt {
    /// Profile to use
    #[structopt(possible_values = &Profile::variants(), case_insensitive = true)]
    profile: Profile,

    /// Number of profiling iterations
    #[structopt(long = "iterations", default_value = "100")]
    iterations: u64,
}

fn main() {
    let Opt {
        profile,
        iterations,
    } = Opt::from_args();
    match profile {
        Profile::DictStringIntPlain => profiles::dict_string_int_plain::exec(iterations),
        Profile::Booleans => profiles::booleans::exec(iterations),
    }
}
