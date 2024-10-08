# Performance Testing
This folder contains notes, scripts, and resources related to performance testing, load generation, and performnace analysis.

## Testing toolkits

| Topic                                                                                                                                  | Description
|----------------------------------------------------------------------------------------------------------------------------------------| -------------------------------------------------------------------------------------
| [**TPCDS at scale with PySpark**](TPCDS_PySpark)                                                                                       | Kit for running TPCDS benchmark queries with PySpark instrumented with sparkMeasure to collect performance metrics.
| **Basic CPU load-testing**<br/>- [**Python CPU est**](Test_CPU_parallel_Python)<br/>- [**Rust CPU test**](Test_CPU_parallel_Rust)<br/> | Kit for load testing and measuring CPU-intensive workloads.<br/> Docs: <br>- [How to use the CPU load-testing kit (blog)](https://db-blog.web.cern.ch/node/189), [(pdf)](https://canali.web.cern.ch/docs/CPU_Load_Testing_Database_Servers_April2023.pdf)
| [**At-scale CPU and memory load testing**](Spark_CPU_memory_load_testkit)                                                              | Kit for load testing CPU and memory-intensive workloads in parallel using Apache Spark. <br/> Docs: <br/>- [CPU performance testing (pdf)](https://canali.web.cern.ch/docs/Spark_CPU_and_memory_load_testing_HDP6_RAC55_May2023.pdf) <br/>- [JDK performance comparisons](Spark_CPU_memory_load_testkit/Test_JDKs) 


## Notes on performance tools
| Topic                                                                                                                                                   | Description
|---------------------------------------------------------------------------------------------------------------------------------------------------------| -------------------------------------------------------------------------------------
| [**Load testing for Oracle**](Oracle_load_testing_with_SLOB)                                                                                            | Example of load testing Oracle logical IO using the SLOB test kit
| [**Tools: Linux memory performance measurement**](Tools_Linux_Memory_Perf_Measure.md)                                                                   | Notes on tools for Linux memory performance measurement
| [**Tools: Systems performance measurements**](Tools_Linux_OS_CPU_Disk_Network.md)                                                                       | Notes on tools for Linux OS, CPU, Disk and Network performance measurement
| [**Tools: Flame Graphs**](Tools_FlameGraphs.md)                                                                                                         | Notes on tools for Flame Graphs generation (C, Java, Python, Linux)