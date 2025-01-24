# Performance Testing
This folder contains notes, scripts, and resources related to performance testing, load generation, and performnace analysis.

## Testing toolkits

- [**Test_CPU_parallel_Rust**](Test_CPU_parallel_Rust)
    - Kit for load testing by generating and measuring CPU-intensive workloads written in Rust.
- [**Test_CPU_parallel_Python**](Test_CPU_parallel_Python)
    - Kit for load testing in Python.
- [**TPCDS at scale with PySpark**](TPCDS_PySpark)    
  - Kit for running TPCDS benchmark queries with PySpark instrumented with sparkMeasure to collect performance metrics.
- [**Spark_CPU_memory_load_testkit**](Spark_CPU_memory_load_testkit)
    - Kit for load testing CPU and memory-intensive workloads in parallel using Apache Spark.

## Notes on Performance Tools
| Topic                                                                                                                                                   | Description
|---------------------------------------------------------------------------------------------------------------------------------------------------------| -------------------------------------------------------------------------------------
| [**Load testing for Oracle**](Oracle_load_testing_with_SLOB)                                                                                            | Example of load testing Oracle logical IO using the SLOB test kit
| [**Tools: Linux memory performance measurement**](Tools_Linux_Memory_Perf_Measure.md)                                                                   | Notes on tools for Linux memory performance measurement
| [**Tools: Systems performance measurements**](Tools_Linux_OS_CPU_Disk_Network.md)                                                                       | Notes on tools for Linux OS, CPU, Disk and Network performance measurement
| [**Tools: Flame Graphs**](Tools_FlameGraphs.md)                                                                                                         | Notes on tools for Flame Graphs generation (C, Java, Python, Linux)