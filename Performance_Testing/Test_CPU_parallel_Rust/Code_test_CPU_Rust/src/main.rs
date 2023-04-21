// This is a smiple program to test CPU speed in Rust
// Luca.Canali@cern.ch, April 2023

extern crate rayon;
extern crate clap;
extern crate statrs;

mod test_cpu_parallel;
use test_cpu_parallel::TestCPUParallel;
use clap::{App, Arg};

fn main() {
    let args = App::new("test_cpu_parallel")
        .version("0.1.0")
        .author("Luca.Canali@cern.ch")
        .about("Basic CPU workload generator")
        .arg(
            Arg::new("full")
                .help("Run a full test, scanning the number of concurrent worker threads from 1 to max_num_workers")
                .required(false)
                .short('f')
                .long("full"),
        )
        .arg(
            Arg::new("num_workers")
                .help("Number of concurrent worker threads")
                .required(false)
                .short('w')
                .long("num_workers")
                .default_value("2"),
        )
        .arg(
            Arg::new("output_file")
                .help("Output CSV file, optional and only used in full mode")
                .required(false)
                .short('o')
                .long("output_file")
                .default_value(""),
        )
        .arg(
            Arg::new("num_job_execution_loops")
                .help("Number of times to execute the job")
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

    println!("Starting a test with num_workers = {}, num_job_execution_loops = {}, worker_inner_loop_size = {}, full = {}, output_file = {:?}",
             num_workers, num_job_execution_loops, worker_inner_loop_size, args.is_present("full"), output_file);
    let test = TestCPUParallel::new(num_workers, num_job_execution_loops, worker_inner_loop_size, output_file);
    // debug
    // let test = TestCPUParallel::new(2, 2, 200000, "".to_string());

    if args.is_present("full") {
        test.test_full();
    } else {
        test.test_one_load(None);
    }
}
