## Load testing CPUs with parallel workers, Rust version

This folder contains a Rust program to load test CPUs and measure job execution time as a function of the number of parallel workers.  
- The tool will produce as output the measurement of the job execution time as a function of the number of parallel workers.  
- When run in full mode, the program will run a range of tests and output a cvs file with the measured values.  
- This folder contains also example data collected with the tool and Jupyter notebooks used to analyze the data.  
- See also the Python version of the same tool: [Test_CPU_parallel_Python](../Test_CPU_parallel_Python)

### Contents
- [**test_cpu_parallel**](test_cpu_parallel) - a binary executable, compiled from Rust to run the load test.
- [**Code_test_CPU_Rust**](Code_test_CPU_Rust) - the source code of the Rust program.
- [**Data**](Data) - example data collected with the tool.
- [**Notebooks**](Notebooks) - Jupyter notebooks used to analyze the collected data.

### Motivations and limitations
  - Use this to generate CPU-intensive load on a system by running multiple threads in parallel.
  - Measure the scalability of the CPU using full mode and the provided analysis notebooks
  - Compare CPU load and scalability across systems
  - This is not a benchmark but rather a tool to generate CPU load and measure the scalability of the CPU on a system 
 
### How to collect CPU load-testing data using [test_cpu_parallel](test_cpu_parallel)
  - Download the [binary executable for Linux from this link](https://canali.web.cern.ch/res/test_cpu_parallel.gz) as in:
    ```
    wget https://canali.web.cern.ch/res/test_cpu_parallel.gz
    gunzip test_cpu_parallel.gz
    chmod +x test_cpu_parallel
    ./test_cpu_parallel -w 2 
    ```
  - Or compile the source code with Rust (see details in the [Code_test_CPU_Rust](Code_test_CPU_Rust) folder)

Example:
```
# run one-off data collection with 2 concurrent workers
./test_cpu_parallel -w 2 

# Measure job runtime over a range of concurrent workers and output the results to a CSV file
./test_cpu_parallel --num_workers 8 --full --output myout.csv 

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

### How to analyze the collected data
When using the tool in full mode, the output is a CSV file with the measured job execution time as a function of the number of parallel workers.  
See the [Notebooks](Notebooks) folder for examples of Jupyter notebooks used to analyze the collected data.  
See the blog entry [CPU Load Testing Exercises: Tools and Analysis for Oracle Database Servers](https://db-blog.web.cern.ch/node/189) for more details
and examples of the analyses and plots that can be produced with the collected data. 