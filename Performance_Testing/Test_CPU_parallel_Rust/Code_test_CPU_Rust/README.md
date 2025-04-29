## CPU load testing kit in Rust
`test_cpu_parallel` is basic CPU workload generator written in Rust.
It runs a CPU-burning loop using multithreading, with configurable parallelism degree.

More Detailed instructions available at [Project homepage:](../README.md)

---- 
Compile the tool using Rust with: `cargo build`
  - Using `cargo build --release` is not recommended for this tool, 
    as the optimizations play against the simple "CPU burning loop" implemented in the tool
  - The Cargo version used for compiling has an impact on the output, notably the performance of the tool.
    - Version 1.3.0, compiled with Cargo version 1.86.0

Note: To compile a Rust project, you need to have the Rust programming language and its associated 
  tools installed on your system. If you haven't installed Rust yet, you can do so by following
  the instructions at https://www.rust-lang.org/tools/install

Examples:
```
# Run data collection with parallelism 2
./test_cpu_parallel -w 2 

# Get the  help message
./test_cpu_parallel --help

Use test_cpu_parallel to generate CPU-intensive load on a system
The tool runs multi-threaded loops with configurable parallelism
Two workload types are implemented: CPU-intensive (default) and memory-intensive
The output reports measurements of the workload execution time as a function of load
Project homepage: https://github.com/LucaCanali/Miscellaneous/tree/master/Performance_Testing/Test_CPU_parallel_Rust

Example:
./test_CPU_parallel --num_workers 2


Usage: test_cpu_parallel [OPTIONS]

Options:
  -f, --full
          Full mode will test all the values of num_workers from 1 to the value set with --num_workers, use this to collect speedup test measurements and create plots, default = False
  -w, --num_workers <num_workers>
          Number of parallel threads running concurrently [default: 2]
  -o, --output_file <output_file>
          Optional output file, applies only to the full mode [default: ]
  -m, --mode <mode>
          Specifies the workload mode: 'cpu' for CPU-intensive or 'memory' for memory-intensive [default: cpu] [possible values: cpu, memory]
      --num_job_execution_loops <num_job_execution_loops>
          Number of times the execution loop is run on each worker [default: 3]
      --worker_inner_loop_size <worker_inner_loop_size>
          Number of iterations in the inner loop of the worker thread [default: 1000]
      --memory_size <memory_size>
          Size of the buffer used by the 'memory' mode in MB, rounded to next power of 2 if needed. [default: 1024]
  -h, --help
          Print help
  -V, --version
          Print version
```
