## CPU load testing kit in Rust
test_cpu_parallel is basic CPU workload generator written in Rust
- It runs a CPU-burning loop concurrently on the system, with configurable parallelism.
- Compile with Rust: `cargo build`
  - note, using `cargo build --release` is not recommended for this tool, 
    as the optimizations play against the simple "CPU burning loop" implemented in the tool
- To compile a Rust project, you need to have the Rust programming language and its associated 
  tools installed on your system. If you haven't installed Rust yet, you can do so by following
  the instructions at https://www.rust-lang.org/tools/install

Examples:
```
# run data collection with parallelism 2
./test_cpu_parallel -w 2 

# Get the help message
./test_cpu_parallel --help
test_cpu_parallel - A basic CPU workload generator written in Rust 1.0.1
Luca.Canali@cern.ch

Use test_cpu_parallel to generate CPU-intensive load on a system by running single-threaded, or with
multiple threads in parallel.
The tool runs a CPU-burning loop concurrently on the system with configurable parallelism.
The tool outputs measurements of the CPU-burning loop execution time as a function of load, to
terminal or to a csv file.

Example:
./test_CPU_parallel --num_workers 2


USAGE:
    test_cpu_parallel [OPTIONS]

OPTIONS:
    -f, --full
            Full mode will test all the values of num_workers from 1 to the value set with
            --num_workers, use this to collect speedup test measurements and create plots, default =
            False

    -h, --help
            Print help information

        --num_job_execution_loops <num_job_execution_loops>
            Number of times the execution loop is run on each worker [default: 3]

    -o, --output_file <output_file>
            Optional output file, applies only to the full mode [default: ]

    -V, --version
            Print version information

    -w, --num_workers <num_workers>
            Number of parallel threads running concurrently [default: 2]

        --worker_inner_loop_size <worker_inner_loop_size>
            Number of iterations in the inner loop of the worker thread [default: 30000]
```
