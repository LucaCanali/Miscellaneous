// test_cpu_parallel - A basic CPU/memory workload generator written in Rust
// Luca.Canali@cern.ch
// Initial release: April 2023
// Last updated: December 2025

use clap::{Parser, ValueEnum};
use test_cpu_parallel::{TestCPUParallel, WorkloadMode};

const ABOUT: &str = r#"
Generate CPU- or memory-intensive load on a system.

The tool runs multi-threaded loops with configurable parallelism.
Two workload types are implemented:
  - cpu    (default): pure CPU-intensive workload
  - memory: memory+CPU workload using a large random-access buffer

The output reports workload execution time statistics at both thread and batch level.

Project homepage:
  https://github.com/LucaCanali/Miscellaneous/tree/master/Performance_Testing/Test_CPU_parallel_Rust

Examples:
  test_cpu_parallel -w 4
  test_cpu_parallel -w 8 --full -o results.csv
  test_cpu_parallel -w 8 -m memory --memory-size 2048
"#;

#[derive(Copy, Clone, Debug, ValueEnum)]
pub enum CliMode {
    Cpu,
    Memory,
}

impl From<CliMode> for WorkloadMode {
    fn from(m: CliMode) -> WorkloadMode {
        match m {
            CliMode::Cpu => WorkloadMode::Cpu,
            CliMode::Memory => WorkloadMode::Memory,
        }
    }
}

#[derive(Parser, Debug)]
#[command(
    name = "test_cpu_parallel",
    version,
    author,
    about = "CPU & memory load generator for quick benchmarking and load testing",
    long_about = ABOUT
)]
struct Cli {
    /// Full sweep: test num_workers = 1..=N instead of only N
    #[arg(short = 'f', long = "full")]
    full: bool,

    /// Number of worker threads to run in parallel
    #[arg(short = 'w', long = "num_workers", default_value_t = 2, value_parser = clap::value_parser!(usize))]
    num_workers: usize,

    /// Optional CSV output file (only used in --full mode)
    #[arg(short = 'o', long = "output_file")]
    output_file: Option<String>,

    /// Workload mode: cpu (default) or memory
    #[arg(short = 'm', long = "mode", value_enum, default_value_t = CliMode::Cpu)]
    mode: CliMode,

    /// Number of batches (outer loops) to run
    #[arg(long = "num_job_execution_loops", default_value_t = 3, value_parser = clap::value_parser!(usize))]
    num_job_execution_loops: usize,

    /// Inner-loop iterations per worker
    #[arg(long = "worker_inner_loop_size", default_value_t = 1000, value_parser = clap::value_parser!(usize))]
    worker_inner_loop_size: usize,

    /// Memory size in MiB for the 'memory' workload (rounded up to next power of two)
    #[arg(long = "memory_size", default_value_t = 1024, value_parser = clap::value_parser!(usize))]
    memory_size: usize,
}

fn main() {
    let cli = Cli::parse();

    println!("test_cpu_parallel - a basic CPU/memory workload generator");
    println!("Use -h / --help for full usage information.\n");

    println!(
        "Parameters:
  num_workers              = {}
  num_job_execution_loops  = {}
  worker_inner_loop_size   = {}
  mode                     = {:?}
  full                     = {}
  output_file              = {:?}
  memory_size (MiB)        = {}
",
        cli.num_workers,
        cli.num_job_execution_loops,
        cli.worker_inner_loop_size,
        cli.mode,
        cli.full,
        cli.output_file,
        cli.memory_size,
    );

    // Map CLI enum to library enum
    let mode: WorkloadMode = cli.mode.into();

    let test = TestCPUParallel::new(
        cli.num_workers,
        cli.num_job_execution_loops,
        cli.worker_inner_loop_size,
        cli.output_file,
        cli.memory_size,
    );

    // Set a handler for Ctrl+C
    ctrlc::set_handler(|| {
        eprintln!("Received Ctrl+C. Exiting.");
        std::process::exit(1);
    })
    .expect("Error setting Ctrl+C handler");

    let result = if cli.full {
        test.test_full(mode)
    } else {
        test.test_one_load(None, mode).map(|_| ())
    };

    if let Err(e) = result {
        eprintln!("Error: {e}");
        std::process::exit(1);
    }
}
