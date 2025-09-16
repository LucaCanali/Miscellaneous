# Performance Troubleshooting and Testing
This folder contains notes, scripts, and resources related to performance testing, load generation, and performnace analysis.

## Toolkits

### [**Test_CPU_parallel_Rust**](Test_CPU_parallel_Rust)
- A toolkit for CPU load testing using **Rust**.
- Generates and measures **CPU-intensive multi-threaded workloads**.
- Designed for evaluating CPU scalability and performance across systems.

### [**Test_CPU_parallel_Python**](Test_CPU_parallel_Python)
- A Python-based toolkit for CPU load testing.

### [**TPC-DS at Scale with PySpark**](TPCDS_PySpark)
- A benchmarking kit for running **TPC-DS benchmark queries** with **Apache Spark**.
- Key features:
    - Written in Python (PySpark).
    - Instrumented with **sparkMeasure** to collect detailed performance metrics.
    - Suitable for testing the scalability and efficiency of Spark clusters.

### [**PyLatencyMap**](PyLatencyMap)
- PyLatencyMap is a terminal-based visualizer for latency histograms.
- It’s intended to help with performance tuning and troubleshooting.
- Works from the command line and plays nicely with sources that output latency histograms (Oracle wait histograms, BPF/bcc, DTrace, SystemTap, tracefiles, etc.).

### [**Spark_CPU_memory_load_testkit**](Spark_CPU_memory_load_testkit)
- A toolkit for generating **CPU- and memory-intensive workloads** using **Apache Spark**.
- Key features:
    - Runs parallel workloads to test Spark cluster performance.
    - Useful for stress-testing distributed systems under heavy CPU and memory usage.
  
---
## Notes on Performance Tools
| Topic                                                                                                                                                   | Description
|---------------------------------------------------------------------------------------------------------------------------------------------------------| -------------------------------------------------------------------------------------
| [**Load testing for Oracle**](Oracle_load_testing_with_SLOB)                                                                                            | Example of load testing Oracle logical IO using the SLOB test kit
| [**Tools: Linux memory performance measurement**](Tools_Linux_Memory_Perf_Measure.md)                                                                   | Notes on tools for Linux memory performance measurement
| [**Tools: Systems performance measurements**](Tools_Linux_OS_CPU_Disk_Network.md)                                                                       | Notes on tools for Linux OS, CPU, Disk and Network performance measurement
| [**Tools: Flame Graphs**](Tools_FlameGraphs.md)                                                                                                         | Notes on tools for Flame Graphs generation (C, Java, Python, Linux)
