## CPU load testing kit in Rust
test_cpu_parallel is simple CPU load test kit
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
./test_cpu_parallel -w2 

./test_cpu_parallel -h
test_cpu_parallel 0.1.0
Luca.Canali@cern.ch
Basic CPU workload generator

USAGE:
    test_cpu_parallel [OPTIONS]

OPTIONS:
    -f, --full
            Run a full test, scanning the number of concurrent worker threads from 1 to
            max_num_workers

    -h, --help
            Print help information

        --num_job_execution_loops <num_job_execution_loops>
            Number of times to execute the job [default: 3]

    -o, --output_file <output_file>
            Output CSV file, optional and only used in full mode [default: ]

    -V, --version
            Print version information

    -w, --num_workers <num_workers>
            Number of concurrent worker threads [default: 2]

        --worker_inner_loop_size <worker_inner_loop_size>
            Number of iterations in the inner loop of the worker thread [default: 200000]
```


