// This is a basic program to test CPU speed in Rust
// Luca.Canali@cern.ch, April 2023

extern crate rayon;
extern crate clap;
extern crate statrs;
extern crate ctrlc;

mod test_cpu_parallel;
use test_cpu_parallel::TestCPUParallel;
use clap::{App, Arg};

fn main() {
    let args = App::new("test_cpu_parallel - A basic CPU workload generator written in Rust")
        .version("1.0.1")
        .author("Luca.Canali@cern.ch")
        .about(r#"
Use test_cpu_parallel to generate CPU-intensive load on a system by running single-threaded, or with multiple threads in parallel.
The tool runs a CPU-burning loop concurrently on the system with configurable parallelism.
The output are measurements of the CPU-burning loop execution time as a function of load, to terminal or to a csv file.
Project homepage: https://github.com/LucaCanali/Miscellaneous/tree/master/Performance_Testing/Test_CPU_parallel_Rust

Example:
./test_CPU_parallel --num_workers 2
        "#)
        .arg(
            Arg::new("full")
                .help("Full mode will test all the values of num_workers from 1 to the value set with --num_workers, use this to collect speedup test measurements and create plots, default = False")
                .required(false)
                .short('f')
                .long("full"),
        )
        .arg(
            Arg::new("num_workers")
                .help("Number of parallel threads running concurrently")
                .required(false)
                .short('w')
                .long("num_workers")
                .default_value("2"),
        )
        .arg(
            Arg::new("output_file")
                .help("Optional output file, applies only to the full mode")
                .required(false)
                .short('o')
                .long("output_file")
                .default_value(""),
        )
        .arg(
            Arg::new("num_job_execution_loops")
                .help("Number of times the execution loop is run on each worker")
                .required(false)
                .long("num_job_execution_loops")
                .default_value("3"),
        )
        .arg(
            Arg::new("worker_inner_loop_size")
                .help("Number of iterations in the inner loop of the worker thread")
                .required(false)
                .long("worker_inner_loop_size")
                .default_value("30000"),
        )
        .get_matches();

    let num_workers = args.value_of("num_workers").unwrap().parse::<usize>().unwrap();
    let num_job_execution_loops = args.value_of("num_job_execution_loops").unwrap().parse::<usize>().unwrap();
    let worker_inner_loop_size = args.value_of("worker_inner_loop_size").unwrap().parse::<usize>().unwrap();
    let output_file = args.value_of("output_file").unwrap().to_string();

    println!("test_cpu_parallel - A basic CPU workload generator written in Rust");
    println!("Use for testing and comparing CPU performance [-h, --help] for help\n");

    println!("Starting a test with num_workers = {}, num_job_execution_loops = {}, worker_inner_loop_size = {}, full = {}, output_file = {:?}",
             num_workers, num_job_execution_loops, worker_inner_loop_size, args.is_present("full"), output_file);
    let test = TestCPUParallel::new(num_workers, num_job_execution_loops, worker_inner_loop_size, output_file);
    // debug
    // let test = TestCPUParallel::new(2, 2, 200000, "".to_string());

    // Set a handler for Ctrl+C
    ctrlc::set_handler(|| {
        println!("Received Control-C. Exiting.");
        std::process::exit(0);
    })
        .expect("Error setting Ctrl+C handler");

    if args.is_present("full") {
        test.test_full();
    } else {
        test.test_one_load(None);
    }
}
