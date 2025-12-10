# 🔥 CPU & Memory Load Testing with Rust – `test_cpu_parallel`
[![crate](https://img.shields.io/crates/v/test_cpu_parallel.svg)](https://crates.io/crates/test_cpu_parallel)


Welcome to `test_cpu_parallel`, a fast, self-contained load generator for benchmarking CPU and memory performance. 
Written in Rust, this tool is ideal for exploring system scalability, evaluating raw CPU throughput, and comparing
hardware or virtualization environments with minimal overhead.

- **Author / Maintainer**: [Luca Canali](mailto:Luca.Canali@cern.ch)
- **Initial Release**: April 2023
- **Latest Version**: 1.3.2 (December 2025)

## 🚀 Key Features

|                           | CPU Mode | Memory Mode |
|---------------------------|:--------:|:-----------:|
| Configurable worker pool  | ✅       | ✅          |
| Adjustable loop size      | ✅       | ✅          |
| Batch statistics (median / mean / σ) | ✅ | ✅ |
| CSV export                | ✅       | ✅          |
| Cross‑platform            | ✅       | ✅          |

---

## 📦 Installation Options

| Method                  | Command                                                                                                                     |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **Linux Binary**        | `curl -O https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel && chmod +x test_cpu_parallel` |
| **Windows Binary**      | `curl -O https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel.exe`                         |
| **Docker**              | `docker run --rm lucacanali/test_cpu_parallel -w 2`                                                                         |
| **Cargo / crates.io**   | `cargo install test_cpu_parallel`                                                                                           |
| **Build locally**       | `git clone this repo + cargo build --release`                                                                               |

---

## ⚡ Quick start

```bash
# Burn CPU with 4 threads
./test_cpu_parallel -w 4

# Run a full scalability test from 1 to 16 threads
./test_cpu_parallel --num_workers 16 --full -o results.csv

# Stress test memory using 8 threads
./test_cpu_parallel -w 8 --mode memory
```
---
 
## 🔧 Command‑line reference

```text
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
## 🎯 Use Cases
- Compare CPU speed across systems and configurations 
  - new system vs. old CPUs, VM/container vs bare-metal performance, etc
  - compare performance over time
- Measure if the available CPU cores correspond to the expected performance
  - e.g. 2 physical cores should provide 2x speedup, 4 cores should provide 4x speedup
- Benchmark raw multithreaded CPU performance
  - Profile speedup curves and find CPU load saturation points
- Test memory throughput under parallel pressure

---
## 📁 Project Structure
- [**Container**](Container): Instructions and a container image for running `test_cpu_parallel` using Docker and Kubernetes.
- [**Code_test_CPU_Rust**](Code_test_CPU_Rust): Source code for the Rust program.
- [**Data**](Data): Example datasets collected using the tool.
- [**Notebooks**](Notebooks): Jupyter notebooks used to analyze the collected data.
 
## 🐧 Running on Linux
There are multiple and alternative ways to deploy the tool, suitable for different use cases:
  - **Run from a container image** using Docker or podman, see [Container](Container) for details
    ```
    # Run with Docker or Podman:
    docker run lucacanali/test_cpu_parallel /opt/test_cpu_parallel -w 2 
    ```
  - **Run the binary executable**
    Download the [binary executable for Linux from this link](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel) and run it as in:
    ```
    wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel
    chmod +x test_cpu_parallel
    ./test_cpu_parallel

    # Note, you can check the integrity of the download with the sha256sum command
    sha256sum test_cpu_parallel
    # Expected output for version 1.3.2:
    4617c06fdbcc4fbcce05f9a5ddd9c733b70c6a5cafd22d1b0090464af6e44e29
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
  - Available binaries for Linux:
    - [test_cpu_parallel v. 1.3.2, Cargo 1.91.1](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.3.2)
    - [test_cpu_parallel v. 1.3.1, Cargo 1.86.0](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.3.1)
    - [test_cpu_parallel v. 1.2.0, Cargo 1.84.0](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.2.0)
    - [test_cpu_parallel v. 1.1.0, Cargo 1.77.1](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.1.0)
    - [test_cpu_parallel v. 1.0.1, Cargo 1.68.21](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.0)

## 🪟 Running on Windows
You can run test_cpu_parallel on Windows via:
- Rust toolchain (native build)
- Windows Subsystem for Linux (WSL)
- Or precompiled binary:
   ```
   curl -O https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel.exe
   test_cpu_parallel.exe -w 2
   ```
 - Optional: validate hash
   ```
   certutil -hashfile test_cpu_parallel.exe SHA256

   Expected SHA256 (v1.3.2):
   503b2e381fa5925c7b02c55d2057875ff9d73e4dc58c666ae3e580175e12d25b
   ```
- Available binaries for Windows:
   - [test_cpu_parallel.exe v. 1.3.2, Cargo 1.91.1](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.3.2.exe)
   - [test_cpu_parallel.exe v. 1.3.1, Cargo 1.86.0](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.3.1.exe)
   - [test_cpu_parallel.exe v. 1.2.0, Cargo 1.84.0](https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel_v1.2.0.exe)

---

## 📊 Output & Analysis

The `--full` sweep writes a tidy CSV.  
For example this run on a server with 32 cores using test_cpu_parallel_v1.3.1:
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
  - Related blogs:
    - [CPU Load Testing Exercises: Tools and Analysis for Oracle Database Servers](https://db-blog.web.cern.ch/node/189) 
    - [Are you Happy with your CPU Performance? Quickly measure and load-test your CPUs with a simple Rust tool](https://externaltable.blogspot.com/2025/12/are-you-happy-with-your-cpus-performance.html)

## Notes
- This is not a full benchmarking suite, it is designed for quick load generation and multithreaded performance evaluation.
- The tool will produce as output the measurement of the job execution time as a function of the number of parallel workers.
- When run in full mode, the program will run a range of tests and output a cvs file with the measured values.
- The folder Data contains examples of measurements collected with the tool and the Jupyter notebooks used to analyze the data.
- See also the Python tool: [Test_CPU_parallel_Python](../Test_CPU_parallel_Python)
