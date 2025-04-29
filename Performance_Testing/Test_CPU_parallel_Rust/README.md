# **Load Testing CPUs - Rust Version**

Welcome to the project home for `test_cpu_parallel`, a fast, self‑contained CPU / memory load generator written in Rust.

**Goal**   Generate reproducible, highly‑parallel workloads so you can **measure raw CPU throughput**, study **scalability**, and compare **hardware & virtualization layers** with minimal friction.

**Contact**: [Luca.Canali@cern.ch](mailto:Luca.Canali@cern.ch)  
**Initial release**: April 2023  
**Latest version**: 1.3.0 (April 2025)

## ✨ Features

|                           | CPU Mode | Memory Mode |
|---------------------------|:--------:|:-----------:|
| Configurable worker pool  | ✅       | ✅          |
| Adjustable loop size      | ✅       | ✅          |
| Batch statistics (median / mean / σ) | ✅ | ✅ |
| CSV export                | ✅       | ✅          |
| Cross‑platform            | ✅       | ✅          |

---

## 📦 Installation

| Method | Command                                                                                                                                         |
|--------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| **Binary (Linux)** | `wget -O test_cpu_parallel https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel && chmod +x test_cpu_parallel` |
| **Docker** | `docker run --rm lucacanali/test_cpu_parallel -w 2`                                                                                             |

> *Windows*: grab [`test_cpu_parallel.exe`](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel.exe) or use WSL + cargo.

---

## ⚡ Quick start

```bash
# run a quick 4‑thread CPU burn
$ test_cpu_parallel -w 4

# explore scalability 1 → 16 threads, save results
$ test_cpu_parallel --num_workers 16 --full -o results.csv

# hammer the memory subsystem with 8 workers
$ test_cpu_parallel -w 8 --mode memory
```
---
 
## 🔧 Command‑line reference

```text
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
          Size of the buffer used by the 'memory' mode in MiB, rounded to next power of 2 if needed. [default: 1024]
  -h, --help
          Print help
  -V, --version
          Print version
```

---
## Goals and Key Features
`test_cpu_parallel` is a low-complexity CPU workload generator designed to:
- **Generate CPU-intensive workloads** for quick and effective testing.
- **Measure multithreaded CPU performance** efficiently.
- **Support configurable parallelism**:
    - Customize the number of concurrent threads and the size of inner loop iterations.
- **Provide detailed performance metrics**:
    - Outputs results to the console or saves them to a CSV file.
    - Metrics are intended for scalability analysis and performance evaluation.
- **Deploy easily across platforms**:
    - Compatible with many Linux distributions and versions.
    - Deployable using Docker or Kubernetes environments.
    - Usable on Windows (natively or via WSL).
- **Note**: This is **not a full benchmarking tool**.  
  It is designed as a quick-load generator to evaluate CPU performance and multithreaded scalability, not to replace structured benchmarking solutions.

## Contents
- [**Container**](Container): Instructions and a container image for running `test_cpu_parallel` using Docker and Kubernetes.
- [**Code_test_CPU_Rust**](Code_test_CPU_Rust): Source code for the Rust program.
- [**Data**](Data): Example datasets collected using the tool.
- [**Notebooks**](Notebooks): Jupyter notebooks used to analyze the collected data.
 
## Get started with test_CPU_parallel on Linux
There are multiple and alternative ways to deploy the tool, suitable for different use cases:
  - **Run from a container image** using Docker or podman, see [Container](Container) for details
    ```
    # Run with Docker or Podman:
    docker run lucacanali/test_cpu_parallel /opt/test_cpu_parallel -w 2 
    ```
  - **Run the binary executable directly**
    Download the [binary executable for Linux from this link](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel) and run it as in:
    ```
    wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel
    chmod +x test_cpu_parallel
    ./test_cpu_parallel

    # Note, you can check the integrity of the download with the sha256sum command
    sha256sum test_cpu_parallel
    # Expected output for version 1.3.0:
    94f904160b0d03dbbd3d6a56892271fc6c82ad09c1ab416fae69a94451a62f2e
    ```
  - **Compile from source** code and run the binary
    - see details in the [Code_test_CPU_Rust](Code_test_CPU_Rust) folder

  - **Run on a Kubernetes cluster** 
    - see also [Container](Container) for details
      ```
      # Run using Kubernetes, basic
      kubectl run test-cpu-parallel --image=lucacanali/test_cpu_parallel --restart=Never -- /opt/test_cpu_parallel -w 2

      kubectl get pods
      kubectl logs -f test-cpu-parallel
      kubectl delete pod test-cpu-parallel
    
      # Use the provided example yaml file to specify CPU requests and limits:
      cd Container
      kubectl apply -f test_cpu_parallel.yaml
      ```
  - Binary versions of the tool for Linux:
    - [test_cpu_parallel v. 1.3.0, Cargo 1.86.0](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.3.0)
    - [test_cpu_parallel v. 1.2.0, Cargo 1.84.0](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.2.0)
    - [test_cpu_parallel v. 1.1.0, Cargo 1.77.1](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.1.0)
    - [test_cpu_parallel v. 1.0.1, Cargo 1.68.21](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.0)

## Windows users
 - Compile and run on Windows using the Rust toolchain.
 - Run using the Windows Subsystem for Linux (WSL)
 - Download the Windows [binary executable from this link](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel.exe):
 - Run the tool from the command line as in:
   ```
   curl - O https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel.exe
   test_cpu_parallel.exe -w 2
   ```
 - Validate the download with:
   ```
   certutil -hashfile test_cpu_parallel.exe SHA256

   The expected output for version 1.3.0:
   503b2e381fa5925c7b02c55d2057875ff9d73e4dc58c666ae3e580175e12d25b
   ```
- Binary versions of the tool for Windows:
   - [test_cpu_parallel.exe v. 1.3.0, Cargo 1.86.0](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.3.0.exe)
   - [test_cpu_parallel.exe v. 1.2.0, Cargo 1.84.0](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.2.0.exe)

---

## 📈 Analysing the output

The `--full` sweep writes a tidy CSV.  
For example this run on a server with 32 cores:
`./test_cpu_parallel -w 16 --worker_inner_loop_size 2000 -f -o CPU_measure_0_16_20250430.csv`

```csv
Threads    Thread-Median Thread-Mean  Thread-Std   Batch-Median Batch-Mean   Batch-Std
----------------------------------------------------------------------------------------
1          19.54        19.54        0.01         19.54        19.54        0.01
2          19.55        19.56        0.03         19.55        19.57        0.03
3          19.47        19.47        0.01         19.48        19.48        0.02
4          19.47        19.47        0.01         19.48        19.48        0.00
5          19.47        19.48        0.03         19.49        19.51        0.04
6          19.47        19.47        0.01         19.48        19.48        0.01
7          19.47        19.49        0.06         19.54        19.58        0.12
8          19.48        19.48        0.02         19.49        19.50        0.02
...
29         20.56        20.67        0.78         21.98        21.98        0.03
30         20.62        20.75        0.83         22.16        22.26        0.69
31         20.67        20.76        0.77         22.05        22.03        0.27
32         21.06        21.04        0.84         22.30        22.42        0.29
```

When using the tool in full mode, the output is a CSV file with the measured job execution time as a function of the number of parallel workers.  
  - This allows for the analysis of the scalability of the system under test. For example, you can plot the speedup or efficiency of the system as a function of the number of workers.
  - See the [Notebooks](Notebooks) folder for examples of Jupyter notebooks used to analyze the collected data.  
  - See the blog entry [CPU Load Testing Exercises: Tools and Analysis for Oracle Database Servers](https://db-blog.web.cern.ch/node/189) for more details
    and examples of the analyses and plots that can be produced with the collected data. 

## Notes
- The tool will produce as output the measurement of the job execution time as a function of the number of parallel workers.
- When run in full mode, the program will run a range of tests and output a cvs file with the measured values.
- The folder Data contains examples of measurements collected with the tool and the Jupyter notebooks used to analyze the data.
- See also the Python tool: [Test_CPU_parallel_Python](../Test_CPU_parallel_Python)
