## Load testing CPUs with parallel workers, Python version
This folder contains a Python script to load test CPUs and measure job execution time as a function of the number of parallel workers  
- The tool will produce as output the measurement of the job execution time as a function of the number of parallel workers.  
- When run in full mode, the script will run a range of tests and output a cvs file with the measured values.  
- This folder contains also example Data collected with the tool and Jupyter notebooks used to analyze the data.  
- See also the Rust version of the same tool: [Test_CPU_parallel_Rust](../Test_CPU_parallel_Rust)

### Contents
- [**test_CPU_parallel.py**](test_CPU_parallel.py) the Python script to run the load test.
- [**Data**](Data) contains example data collected with the tool.
- [**Notebooks**](Notebooks) contains Jupyter notebooks used to analyze the collected data.

### Motivations and limitations
  - Use this to generate CPU-intensive load on a system by running multiple threads in parallel.
  - Measure the scalability of the CPU using full mode and the provided analysis notebooks
  - Compare CPU load and scalability across systems
    - Note that when comparing different systems you want to use the same Python and glibc versions, as these can affect the results
  - This is not a benchmark but rather a tool to generate CPU load and measure the scalability of the CPU on a system

### How to collect CPU load-testing data using [test_CPU_parallel.py](test_CPU_parallel.py):
  - Download the [script from this link](https://raw.githubusercontent.com/LucaCanali/Miscellaneous/master/Performance_Testing/Test_CPU_parallel_Python/test_CPU_parallel.py)
  - Or clone this repository and run the script from the [Performance_Testing/Test_CPU_parallel_Python](.) folder
  - Run the script with the desired parameters, see below for examples
```
test_CPU_parallel.py - A basic CPU workload generator.
Luca.Canali@cern.ch - April 2023

Use this to generate CPU-intensive load on a system, running multiple threads in parallel.
The tool runs a CPU-burning loop concurrently on the system, with configurable parallelims.
The tool outputs a measurement of the CPU-burning loop execution time as function of load.

Examples:
# run one-off data collection with 2 concurrent workers
./test_CPU_parallel.py --num_workers 2 

# Measure job runtime over a range of concurrent workers and output the results to a CSV file
./test_CPU_parallel.py --num_workers 8 --fulll --output myout.csv 

Parameters:

--full - Full mode will test all the values of num_workers from 1 to the value 
         set with --num_workers, use this to collect speedup test measurements and create plots, default = False
--output - Optional output file, applies only to the full mode, default = None
--num_workers - Number of parallel threads running concurrently, default = 2
--num_job_execution_loops - number of times the execution loop is run on each worker, default = 3
--worker_inner_loop_size - internal weight of the inner execution loop, default = 100000000
```

### How to analyze the collected data
When using the tool in full mode, the output is a CSV file with the measured job execution time as a function of the number of parallel workers.  
See the [Notebooks](Notebooks) folder for examples of Jupyter notebooks used to analyze the collected data.  
See the blog entry [CPU Load Testing Exercises: Tools and Analysis for Oracle Database Servers](https://db-blog.web.cern.ch/node/189) for more details
and examples of the analyses and plots that can be produced with the collected data. 