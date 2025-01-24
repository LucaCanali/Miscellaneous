// This is a basic program to test CPU speed in Rust
// Luca.Canali@cern.ch
// April 2023
// Last updated, January 2025

extern crate rayon;
extern crate clap;
extern crate statrs;
extern crate ctrlc;

mod test_cpu_parallel;
use test_cpu_parallel::TestCPUParallel;
use clap::{Command, Arg};

fn main() {
    let args = Command::new("test_cpu_parallel - A basic CPU workload generator written in Rust")
        .version("1.2.0")
        .author("Luca.Canali@cern.ch")
        .about(r#"
Use test_cpu_parallel to generate CPU-intensive or memory-intensive load on a system by running single-threaded, or with multiple threads in parallel.
The tool runs a workload loop concurrently on the system with configurable parallelism.
The output includes measurements of the workload execution time as a function of load, to terminal or to a CSV file.
Project homepage: https://github.com/LucaCanali/Miscellaneous/tree/master/Performance_Testing/Test_CPU_parallel_Rust

Example:
./test_CPU_parallel --num_workers 2 --mode cpu
        "#)
        .arg(
            Arg::new("full")
                .help("Full mode will test all the values of num_workers from 1 to the value set with --num_workers, use this to collect speedup test measurements and create plots, default = False")
                .short('f')
                .long("full")
                .action(clap::ArgAction::SetTrue),
        )
        .arg(
            Arg::new("num_workers")
                .help("Number of parallel threads running concurrently")
                .short('w')
                .long("num_workers")
                .default_value("2"),
        )
        .arg(
            Arg::new("output_file")
                .help("Optional output file, applies only to the full mode")
                .short('o')
                .long("output_file")
                .default_value(""),
        )
        .arg(
            Arg::new("mode")
                .help("Specifies the workload mode: 'cpu' for CPU-intensive or 'memory' for memory-intensive")
                .short('m')
                .long("mode")
                .default_value("cpu")
                .value_parser(["cpu", "memory"]),
        )
        .arg(
            Arg::new("num_job_execution_loops")
                .help("Number of times the execution loop is run on each worker")
                .long("num_job_execution_loops")
                .default_value("3"),
        )
        .arg(
            Arg::new("worker_inner_loop_size")
                .help("Number of iterations in the inner loop of the worker thread")
                .long("worker_inner_loop_size")
                .default_value("1000"),
        )
        .get_matches();

    let num_workers = args
        .get_one::<String>("num_workers")
        .unwrap()
        .parse::<usize>()
        .unwrap();
    let num_job_execution_loops = args
        .get_one::<String>("num_job_execution_loops")
        .unwrap()
        .parse::<usize>()
        .unwrap();
    let worker_inner_loop_size = args
        .get_one::<String>("worker_inner_loop_size")
        .unwrap()
        .parse::<usize>()
        .unwrap();
    let output_file = args
        .get_one::<String>("output_file")
        .unwrap_or(&"".to_string())
        .to_string();
    let mode = args.get_one::<String>("mode").unwrap();

    println!("test_cpu_parallel - A basic CPU workload generator written in Rust");
    println!("Use for testing and comparing CPU or memory performance [-h, --help] for help\n");

    println!(
        "Starting a test with num_workers = {}, num_job_execution_loops = {}, worker_inner_loop_size = {}, mode = {}, full = {}, output_file = {:?}",
        num_workers,
        num_job_execution_loops,
        worker_inner_loop_size,
        mode,
        args.get_flag("full"),
        output_file
    );

    let test = TestCPUParallel::new(
        num_workers,
        num_job_execution_loops,
        worker_inner_loop_size,
        output_file,
    );

    // Set a handler for Ctrl+C
    ctrlc::set_handler(|| {
        println!("Received Control-C. Exiting.");
        std::process::exit(1);
    })
    .expect("Error setting Ctrl+C handler");

    if args.get_flag("full") {
        match test.test_full(mode) {
            Ok(_) => println!("Full test completed successfully."),
            Err(e) => {
                eprintln!("Error during full test: {}", e);
                std::process::exit(1);
            }
        }
    } else {
        match test.test_one_load(None, mode) {
            Ok((median, mean, stdev)) => {
                println!("Single test completed successfully.");
                println!("Median: {:.2}s, Mean: {:.2}s, StdDev: {:.2}s", median, mean, stdev);
            }
            Err(e) => {
                eprintln!("Error during single test: {}", e);
                std::process::exit(1);
            }
        }
    }
}
