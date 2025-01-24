## Load testing CPUs, Rust version

`test_cpu_parallel` is a Rust program designed to load test CPUs and measure job execution times as
a function of the number of parallel workers. It provides insights into CPU scalability and performance
under varying workloads.

---

## **Contents**
- [**Container**](Container): Instructions and a container image for running `test_cpu_parallel` using Docker and Kubernetes.
- [**Code_test_CPU_Rust**](Code_test_CPU_Rust): Source code for the Rust program.
- [**Data**](Data): Example datasets collected using the tool.
- [**Notebooks**](Notebooks): Jupyter notebooks used to analyze the collected data.

---

## **Motivations and Limitations**
- Use this tool to generate CPU-intensive load on a system by running multiple threads in parallel.
- Measure CPU scalability using full mode and analyze the results using the provided Jupyter notebooks.
- Compare CPU load and scalability across different systems.
- This is not intended to be a benchmark but rather a tool for generating load and evaluating CPU scalability.

### Notes
- The tool will produce as output the measurement of the job execution time as a function of the number of parallel workers.  
- When run in full mode, the program will run a range of tests and output a cvs file with the measured values.  
- This folder contains also example data collected with the tool and Jupyter notebooks used to analyze the data.  
- See also the Python version of the same tool: [Test_CPU_parallel_Python](../Test_CPU_parallel_Python)
 
### Multiple ways to deploy [test_cpu_parallel](test_cpu_parallel)
  - **Run from a container image** using Docker or podman, see [Container](Container) for details
    ```
    # Run with Docker or Podman:
    docker run lucacanali/test_cpu_parallel /opt/test_cpu_parallel -w 2 
    ```
  - **Run directly the binary executable**
    Download the [binary executable for Linux from this link](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel) and run it as in:
    ```
    wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel
    chmod +x test_cpu_parallel
  
    # Checksum:
    # sha256sum test_cpu_parallel
    # 6feabf4c59765e463e65e7150cd5636063af9d946ab56b8b5b45151b712d27e2
    ```
  - **Compile from source** code and run the binary, see details in the [Code_test_CPU_Rust](Code_test_CPU_Rust) folder

  - **Run on a Kubernetes cluster** see also [Container](Container) for details
    ```
    # Run using Kubernetes, basic
    kubectl run test-cpu-parallel --image=lucacanali/test_cpu_parallel --restart=Never -- /opt/test_cpu_parallel -w 2

    kubectl get pods
    kubectl logs -f test-cpu-parallel
    kubectl delete pod test-cpu-parallel
    
    # Use a yaml file to specify CPU requests and limits:
    cd Container
    kubectl apply -f test_cpu_parallel.yaml
    
    ```

Examples:
```
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel
chmod +x test_cpu_parallel

# run one-off data collection with 2 concurrent workers
./test_cpu_parallel -w 2 

# Measure job runtime over a ramp of concurrent workers from 1 to 8, and output the results to a CSV file
./test_cpu_parallel --num_workers 8 --full -o myout.csv 

# Get the help message

./test_cpu_parallel --help
Use test_cpu_parallel to generate CPU-intensive or memory-intensive load on a system by running single-threaded, or with multiple threads in parallel.
The tool runs a workload loop concurrently on the system with configurable parallelism.
The output includes measurements of the workload execution time as a function of load, to terminal or to a CSV file.
Project homepage: https://github.com/LucaCanali/Miscellaneous/tree/master/Performance_Testing/Test_CPU_parallel_Rust

Example:
./test_CPU_parallel --num_workers 2 --mode cpu


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
  -h, --help
          Print help
  -V, --version
          Print version
```

### How to analyze the collected data
When using the tool in full mode, the output is a CSV file with the measured job execution time as a function of the number of parallel workers.  
See the [Notebooks](Notebooks) folder for examples of Jupyter notebooks used to analyze the collected data.  
See the blog entry [CPU Load Testing Exercises: Tools and Analysis for Oracle Database Servers](https://db-blog.web.cern.ch/node/189) for more details
and examples of the analyses and plots that can be produced with the collected data. 
