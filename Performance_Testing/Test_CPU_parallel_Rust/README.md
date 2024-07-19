## Load testing CPUs, Rust version

This is the home of test_cpu_parallel, a Rust program to load test CPUs and measure job execution time as a function 
of the number of parallel workers.  

### Contents
- [**Container**](Container) - a container image and instructions for running test_cpu_parallel using Docker and Kubernetes
- [**Code_test_CPU_Rust**](Code_test_CPU_Rust) - the source code of the Rust program
- [**Data**](Data) - example data collected with the tool
- [**Notebooks**](Notebooks) - Jupyter notebooks used to analyze the collected data

### Motivations and limitations
  - Use this to generate CPU-intensive load on a system by running multiple threads in parallel.
  - Measure the scalability of the CPU using full mode and the provided analysis notebooks
  - Compare CPU load and scalability across systems
  - This is not a benchmark but rather a tool to generate CPU load and measure the scalability of the CPU on a system 

### Notes
- The tool will produce as output the measurement of the job execution time as a function of the number of parallel workers.  
- When run in full mode, the program will run a range of tests and output a cvs file with the measured values.  
- This folder contains also example data collected with the tool and Jupyter notebooks used to analyze the data.  
- See also the Python version of the same tool: [Test_CPU_parallel_Python](../Test_CPU_parallel_Python)
 
### How to run [test_cpu_parallel](test_cpu_parallel)
  - **Run from a container image** using Docker or Kubernetes, see [Container](Container) for details
    ```
    # Run with docker or podman:
    docker run lucacanali/test_cpu_parallel /opt/test_cpu_parallel -w 2 
    ```
    ```
    # Run using Kubernetes
    kubectl run test-cpu-parallel --image=lucacanali/test_cpu_parallel --restart=Never -- /opt/test_cpu_parallel -w 2

    kubectl get pods
    kubectl logs test-cpu-parallel
    kubeclt delete pod test-cpu-parallel
    ```
  - Download and run the binary: download the [binary executable for Linux from this link](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel) as in:
    ```
    wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel
    chmod +x test_cpu_parallel
    ./test_cpu_parallel -w 2 
    
    # Checksum:
    # sha256sum test_cpu_parallel
    # 30d9782e35bb840f2054375ec438670f32d5e07b3c4565cdfc2461176f04ed91
    ```
  - Compile from source code and run the binary, see details in the [Code_test_CPU_Rust](Code_test_CPU_Rust) folder

Example:
```
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel
chmod +x test_cpu_parallel

# run one-off data collection with 2 concurrent workers
./test_cpu_parallel -w 2 

# Measure job runtime over a ramp of concurrent workers from 1 to 8, and output the results to a CSV file
./test_cpu_parallel --num_workers 8 --full -o myout.csv 

# Get the help message
./test_cpu_parallel --help
test_cpu_parallel - A basic CPU workload generator written in Rust 1.1.0
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

### How to analyze the collected data
When using the tool in full mode, the output is a CSV file with the measured job execution time as a function of the number of parallel workers.  
See the [Notebooks](Notebooks) folder for examples of Jupyter notebooks used to analyze the collected data.  
See the blog entry [CPU Load Testing Exercises: Tools and Analysis for Oracle Database Servers](https://db-blog.web.cern.ch/node/189) for more details
and examples of the analyses and plots that can be produced with the collected data. 
