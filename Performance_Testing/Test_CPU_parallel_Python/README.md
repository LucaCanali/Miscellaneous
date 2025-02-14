## Load testing CPUs, Python version

This is the home of test_CPU_parallel.py, a Python script to load test CPUs and measure
job execution time as a function of the number of parallel workers.  

### Contents
- [**test_CPU_parallel/test_CPU_parallel.py**](test_CPU_parallel/test_CPU_parallel.py) - the Python package and script used run the load test.
- [**Data**](Data) - Data collected with the tool for CPU comparison tests.
- [**Notebooks**](Notebooks) -  Jupyter notebooks used to analyze the collected data for CPU comparison tests.

### Motivations and limitations
  - Use this to generate CPU-intensive load on a system by running multiple threads in parallel.
  - Measure the scalability of the CPU using full mode and the provided analysis notebooks
  - Compare CPU load and scalability across systems
    - Note that when comparing different systems you want to use the same Python and glibc versions, as these can affect the results
  - This is not a benchmark but rather a tool to generate CPU load and measure the scalability of the CPU on a system

### Notes
- The tool will produce as output the measurement of the job execution time as a function of the number of parallel workers.  
- When run in full mode, the script will run a range of tests and output a cvs file with the measured values.  
- This folder contains also example Data collected with the tool and Jupyter notebooks used to analyze the data.  
- See also the Rust version of this tool: [Test_CPU_parallel_Rust](../Test_CPU_parallel_Rust)

### How to install and run [**test_CPU_parallel.py**](test_CPU_parallel/test_CPU_parallel.py) for load testing:
  - Local install:
    - Option 1. `pip install test_CPU_parallel`
    - or download the [script from this link](https://raw.githubusercontent.com/LucaCanali/Miscellaneous/master/Performance_Testing/Test_CPU_parallel_Python/test_CPU_parallel/test_CPU_parallel.py)
    - or clone this repository and pip install or run the script from the [Performance_Testing/Test_CPU_parallel_Python](.) folder
    - Run the script `test_CPU_parallel.py` with the desired parameters, see below for examples
  - Container:
    - `docker run lucacanali/test_cpu_parallel.py:py3.11 test_CPU_parallel.py`
    - See also [Container](Container) for more details on how to build container images for this tool
      and on how to run it using Docker or Kubernetes

### test_CPU_parallel.py runtime options

- Run the following on local resources or cloud, for example use GitHub Codespaces from this repo
  - [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/LucaCanali/Miscellaneous?devcontainer_path=.devcontainer%2Ftest_CPU_parallel_python%2Fdevcontainer.json)

```
test_CPU_parallel.py --help

test_CPU_parallel.py - A basic CPU workload generator.
Luca.Canali@cern.ch - April 2023

Use test_cpu_parallel to generate CPU-intensive load on a system by running single-threaded, or with multiple threads in parallel.  
The tool runs a CPU-burning loop concurrently on the system with configurable parallelism.  
The output are measurements of the CPU-burning loop execution time as a function of load, printed to terminal, or to a csv file,
or returned programmatically when used as a Python library.  

Example:
# Install from PyPi with pip or clone from GitHub
pip install test-CPU-parallel

# run one-off data collection with 2 concurrent workers
test_CPU_parallel.py --num_workers 2 

# Measure job runtime over a ramp of concurrent workers from 1 to 8, and output the results to a CSV file
test_CPU_parallel.py --num_workers 8 --full --output myout.csv 

Parameters:

--full - Full mode will test all the values of num_workers from 1 to the value 
         set with --num_workers, use this to collect speedup test measurements and create plots, default = False
--output - Optional output file, applies only to the full mode, default = None
--num_workers - Number of parallel threads running concurrently, default = 2
--num_job_execution_loops - number of times the execution loop is run on each worker, default = 3
--worker_inner_loop_size - internal weight of the inner execution loop, default = 100000000
```

### How to use test_CPU_parallel programmatically
You have the ability to employ the test_CPU_parallel function within your Python scripts, including its integration 
into Continuous Integration (CI) tests. This proves advantageous for tasks like quantifying system performance and 
assessing how well the CPU adapts to varying workloads. This becomes especially handy when you're comparing test runs
conducted on different occasions or on distinct computer setups.  
In your code, the process of executing the test and obtaining results is as follows:
```
pip install test-CPU-parallel
from test_CPU_parallel import test_CPU_parallel

# See also the configuration options in the help
test = test_CPU_parallel()

# Run a test
test.test_one_load()

# Run a full run
test.test_full()
```
---
## Python Version and Performance Considerations

The script `test_CPU_parallel.py` is written in Python, and multiple factors can impact its performance.

### Key Factors Affecting Performance:

1. **Python Version**: Different versions can lead to variations in performance.
2. **glibc Version**: The version of glibc in use can also influence performance.
3. **Hardware and System Load**:
    - **CPU Speed**
    - **Number of CPU Cores vs. Test Load**: The ratio of available cores to the test load.
    - **System Load**: The overall load on the system can affect the test.

⚠️ **Caution**: When comparing results across different systems, keep these factors in mind. 
You may also consider comparing with the Rust version of this tool, [Test_CPU_parallel_Rust](../Test_CPU_parallel_Rust).

### Example Results:

The following table displays the performance of `test_CPU_parallel.py` using various Python versions on a specific test system:

> **Test System Configuration**:
> - **HOST CPU**: 4-core CPU E5-1630 v3 @ 3.70GHz
> - **HOST OS**: AlmaLinux 9.5
> - **Docker Images**: Based on alpine3.21

Tests were initiated with the command:
```
IMAGE=lucacanali/test_cpu_parallel.py:py3.11
docker run $IMAGE test_CPU_parallel.py
```

| Python version | Median job runtime (s) | docker image name                             |
|----------------|------------------------|-----------------------------------------------|
| 3.9.21         | 38 sec                 | IMAGE=lucacanali/test_cpu_parallel.py:py3.9   |
| 3.10.16        | 37 sec                 | IMAGE=lucacanali/test_cpu_parallel.py:py3.10  |
| 3.11.11        | 29 sec                 | IMAGE=lucacanali/test_cpu_parallel.py:py3.11  |
| 3.12.8         | 41 sec                 | IMAGE=lucacanali/test_cpu_parallel.py:py3.12  |
| 3.13.1         | 41 sec                 | IMAGE=lucacanali/test_cpu_parallel.py:py3.13  |

Note: While there seems to be a general trend of improved runtime performance (for this simple test) with newer Python versions,
the results for Python 3.12 buck this trend (see a discussion on this on [stackoverflow](https://stackoverflow.com/questions/77230983/why-does-it-take-longer-to-execute-a-simple-for-loop-in-python-3-12-than-in-pyth)).
It's important to recognize that multiple variables might 
influence these results and that these results should not be used as a Python benchmark. 

---   
### How to analyze data collected in full mode
When using the tool in full mode, the output is a CSV file with the measured job execution time as a function of the number of parallel workers.  
- See the [Notebooks](Notebooks) folder for examples of Jupyter notebooks used to analyze the collected data.  
- See the blog entry [CPU Load Testing Exercises: Tools and Analysis for Oracle Database Servers](https://db-blog.web.cern.ch/node/189) for more details
  and examples of the analyses and plots that can be produced with the collected data. 
