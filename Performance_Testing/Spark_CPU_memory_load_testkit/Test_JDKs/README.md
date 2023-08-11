# JDK performance compared using a Spark-based load testing toolkit 

This note reports on load-testing using CPU-intensive workloads generated with Apache Spark.  
You will find tests and measurements comparing 5 different JDKs for running Apache Spark.    
You will find details on the testing methodology, the tools used, and the results obtained for different JDKs.    
Note: this is not a benchmark, the results are not intended to be used for a general evaluation of the performance
of different JDKs, they only reflect the performance of the stress test toolkit and test system used.

## On the testing tool and instrumentation
**What is being measured:**  
- this is a microbenchmark of CPU and memory bandwidth, the tool is not intended to measure the performance of Spark SQL.
- this follows the general ideas of active benchmarking: a load generator is used to produce CPU and memory-intensive load,
while the load is measured with instrumentation.

**Why testing with a CPU and memory-intensive workload:**    
In real life, the CPU and memory intensive workloads are often the most critical ones. In particular, when working with
large datasets in Parquet format, the CPU and memory-intensive workloads are often the most critical ones.
Moreover, workloads that include I/O time from object storage can introduce a lot of variability in the results that 
does not reflect the performance of Apache Spark but rather of the object storage system.
Working on a single large machine also reduces the variability of the results and makes it easier to compare the
performance of different test configurations.

**The test kit:**  
The testing toolkit used for this exercise is described at [test_Spark_CPU_memory](../README.md).
- The tool generates CPU and memory-intensive load, with a configurable number of concurrent workers.  
- It works by reading a large Parquet file. The test setup is such that the file is cached in the system memory
therefore the tool mostly stresses CPU and memory bandwidth.

**Instrumentation:**  
The workload is mostly CPU-bound, therefore the main metrics of interest are CPU time and elapsed time.
Using sparkMeasure, we can also collect metrics on the Spark executors, notably the executors' cumulative elapsed time,
CPU time, and time in garbage collection.

**Workload data:**  
The test data used to generate the workload is a large Parquet table, store_sales, taken from the open source TPCDS benchmark.
The size of the test data is 200 GB, and it is stored in multiple Parquet files.  
The files are cached in the filesystem cache, so that the test kit mostly stresses CPU and memory bandwidth (note,
this requires 512GB of RAM on the test system, if you have less RAM, reduce the dataset size).

**Test results:**  
Tests were run using the script [spark_test_JDKs.sh](Data/spark_test_JDKs.sh) that runs [test_Spark_CPU_memory.py](../test_Spark_CPU_memory.py)
with different JDKs and prints out the results.
The output of three different test were collected and stored in txt files that can be found in the [Data](Data) folder.

**Test system:**  
A server with dual CPUS (AMD Zen 2 architecture), 16 physical cores each, 512 GB RAM, ~300 GB of storage space.

**Spark configuration:**  
We use Apache Spark run in local mode (that is on a single machine, not scaling out on a cluster) for these tests,
with 64GB of heap memory and 20 cores allocated to Spark.
The large heap memory allocation is to reduce Garbage Collection overhead, which still fits in the available RAM.  
The number of cores for Spark (that is the maximum number of concurrent tasks being executed by Spark) is set to 20, 
which brings the CPU load during the test execution to use about 60% of the physical cores, the workload keeps the 
CPUs busy with processing Parquet files, the rest of the CPU power is available for running other accessory load, notably
Garbage collection activities, the OS and other processes.

**Example performance test results:**    
This shows how you can use the toolkit to run the performance tests and collect performance measurements: 
```
$ export JAVA_HOME=.... # Set the JDK that will be used by Spark
$ ./test_Spark_CPU_memory.py --num_workers 20 # Run the 3 tests using 20 concurrent workers (Spark cores)

Allocating a Spark session in local mode with 20 concurrent tasks
Heap memory size = 64g, data_path = ./store_sales.parquet
sparkmeasure_path = ./spark-measure_2.12-0.23.jar
Scheduling job number 1
Job finished, job_run_time (elapsed time) = 38.01 sec
...executors Run Time = 725.99 sec
...executors Cpu Time = 691.41 sec
...executors jvmGC Time = 22.33 sec
Scheduling job number 2
Job finished, job_run_time (elapsed time) = 34.08 sec
...executors Run Time = 671.8 sec
...executors Cpu Time = 660.15 sec
...executors jvmGC Time = 11.13 sec
Scheduling job number 3
Job finished, job_run_time (elapsed time) = 34.02 sec
...executors Run Time = 671.19 sec
...executors Cpu Time = 659.66 sec
...executors jvmGC Time = 11.39 sec
```

**Notes:**  
The elapsed time and the Run time decrease with each test run, in particular from the first to the second run we see a noticeable improvement, 
this is because various internal Spark structures are being "warmed up" and cached.
In all cases, data is read from the Filesystem cache, except for the first warm-up runs that are discarded.
Therefore, the test kit mostly stresses CPU and memory bandwidth.
For the test results and comparisons, we will use the values measured at the 3rd run of each test and average over the
available test results for each category (6 test runs).

## JDK comparison tests
The following tests compare the performance of 5 different JDKs, running on Linux (CentOS 7.9),
on a server with dual Zen 2 CPUs, 16 physical cores each, 512 GB RAM, 300 GB of storage space for the test data.
The Apache Spark version is 3.4.1 the test kit is [test_Spark_CPU_memory.py](../test_Spark_CPU_memory.py).
The JDK tested are:
- openlogic-openjdk-8u372-b07-linux-x64
- openlogic-openjdk-11.0.19+7-linux-x64
- openlogic-openjdk-17.0.7+7-linux-x64
- Oracle's jdk-17.0.8
- Oracle's graalvm-jdk-17.0.8+9.1

The openJDKs were downloaded from [OpenLogic JDK](https://www.openlogic.com/openjdk-downloads), 
the Oracle JDKs were downloaded from [Oracle JDK](https://www.oracle.com/java/technologies/downloads/).    
The OpenLogic OpenJDK are free to use (see website).  
Notably, the Oracle download page also reports that the JDK binaries are free to use in production and free to redistribute, at no cost,
under the Oracle No-Fee Terms and Conditions, and the GraalVM Free Terms and Conditions, respectively, see Oracle's webpage for details.

## Test results and measurements
Test results summarized in this table are from the test output files, see [Data](Data).
The values reported here are taken from the test reports, measured at the 3rd run of each test, as the run time improves when running 
the tests a couple of times in a row (as internal structures and caches are warming up, for example), The results are further averaged over the
available test results (6 test runs) and reported for each category. 


| JDK and Metric name                           | **OpenJDK Java 8**          | **OpenJDK Java 11**         | **OpenJDK Java 17**        | **Oracle Java 17**  | **GraalVM Java 17**             | 
|-----------------------------------------------|-----------------------------|-----------------------------|----------------------------|---------------------|---------------------------------|
| JDK                                           | openlogic-openjdk-8u372-b07 | openlogic-openjdk-11.0.19+7 | openlogic-openjdk-17.0.7+7 | Oracle's jdk-17.0.8 | Oracle's graalvm-jdk-17.0.8+9.1 |
| **Elapsed time (sec)**                        | **39.0**                    | **34.0**                    | **35.2**                   | **34.8**            | **28.9**                        |
| Executors' cumulative <br> ... run time (sec) | 770.4                       | 670.6                       | 695.0                      | 688.3               | 571.0                           |
| ... CPU time (sec)                            | 733.0                       | 659.1                       | 669.7                      | 663.3               | 548.9                           |
| ... Garbage Collection time (sec)             | 35.3                        | 11.3                        | 25.6                       | 25.3                | 22.4                            |


## Performance data analysis
From the metrics and elapsed time measurements reported above, the key findings are:
 - Java 8 has the slowest elapsed time, Java 11 and 17 are about 10% faster than Java 8, GraalVM is about 25% faster than Java 8.
 - The workload is CPU bound. 

The instrumentation metrics provide additional clues on understanding the workload and its performance: 
- `Run time`, reports the cumulative elapsed time for the executors
- `CPU time` reports the cumulative time spent on CPU.
- `Garbage Collection Time` is the time spent by the executors on JVM Garbage collection, and it is a subset of the "Run time" metric.
- From the measured values (see table above) we can conclude that the executors spend most of the time running tasks "on CPU", with some time spent on Garbage collection
- We can see some fluctuations on Garbage Collection time, with Java 8 having the longest GC time. Note that the algorithm G1GC was used in all the tests (its use is set
- as a configuration by the load generation tool [test_Spark_CPU_memory.py](../test_Spark_CPU_memory.py)).
- We can see the GraalVM 17 stands out as having the shorted Executors' runtime. We can speculate that is due to the GraalVM just-in-time compiler and the Native Image feature,
  which provide several optimizations compared to the standard HotSpot JVM (note, before running to install GraalVM for your Spark jobs, please note that there are other factors
  at play here, including that Native Image feature in an optional early adopter technology, see Oracle documentation for details).
- Java 8 shows the worst performance in terms of run time and CPU time, and it also has the longest Garbage Collection time. This is not surprising as Java 8 is the oldest
  of the JDKs tested here, and it is known to have worse performance than newer JDKs.
- Java 11 and Java 17 have similar performance, with Java 11 being a bit faster than Java 17 (of the order of 3% for this workload), at this stage it is not clear if there
  is a fundamental reason for this or the difference comes from measurement noise (see also the section on "sanity checks" and the comments there on errors in the metrics measurements).

## Active benchmarking and sanity checks
The key idea of active benchmarking is that while the load testing tool is running, we also take several measurements and metrics using a variety of
monitoring and measuring tools, for OS metrics and application-specific metrics. These measurements are used to complement the analysis results, 
provide sanity checks, and in general to help understand the performance of the system under test (why is the performance that we see what it is? why not higher/lower?
Are there any bottlenecks or other issues/errors limiting the performance?).
  
**Spark tools:** the application-specific instrumentation used for these tests were the Spark WebUI and the instrumentation with [sparkMeasure](https://github.com/LucaCanali/sparkMeasure)
that allowed us to understand the workload as CPU-bound and to measure the CPU time and Garbage collection time.  

**Java FlameGraph:** Link to a [FlameGraph of the execution profile](http://canali.web.cern.ch/svg/FlameGraph_test_Spark_CPU_memory.html) taken 
during a test run of [test_Spark_CPU_memory.py](../test_Spark_CPU_memory.py).
The FlameGraph shows that the workload is CPU-bound, and that the time is spent in the Spark SQL code, in particular in the Parquet reader.
FlameGraphs are a visualization tool for profiling the performance of applications, see also [Tools_FlameGraphs.md](../../Tools_FlameGraphs.md).

**OS Tools:** (see also [OS monitoring tools](https://github.com/LucaCanali/Miscellaneous/blob/master/Performance_Testing/Tools_Linux_OS_CPU_Disk_Network.md)):
Another important aspect was to ensure that the data was cached in the filesystem cache, to avoid the overhead of reading from disk,
for this tools like `iostat` and `iotop` were used to monitor the disk activity and ensure that the I/O on the system was minimal,
therefore implying that data was read from the filesystem cache.  
A more direct measurement was taken using `cachestat`, a tool that can be found in the perf-tools collection and bcc-tool, 
which allows measuring how many reads hit the filesystem cache, we could see that the hit rate was 100%,
after the first couple of runs that populated the cache (and that were not taken in consideration for the test results).  
CPU measurements were taken using `top`, `htop`, and `vmstat` to monitor the CPU usage and ensure that the CPUs were not saturated.

**Other sanity checks:** were about checking that the intended JDK was used in a given test, for that we used `top` and `jps`, for example.     
Another important check is about the stability of the performance tests' measurements.
We notice fluctuations in the execution time for different runs with the same parameters, for example.
For this reason the load-testing tool is run on a local machine rather than a cluster, where these differences are amplified, moreover the tests are run multiple times,
and the results reported are averages. We estimated the errors in the metrics measurements due to these fluctuations to be less than 3%, see also the raw test results reported
available at [Data](Data).

## Related work

The following references provide additional information on the topics covered in this note.
- [test_Spark_CPU_memory.py](../test_Spark_CPU_memory.py) used to test CPU performance on two difference architectures 
  - see [CPU and Memory testing with Spark](../Spark_CPU_memory_load_testkit/Test_CPUs) and [pdf](https://canali.web.cern.ch/docs/Spark_CPU_and_memory_load_testing_HDP6_RAC55_May2023.pdf)
- CPU load-testing kit
  - [Python version](../../Test_CPU_parallel_Python)
  - [Rust version](../../Test_CPU_parallel_Rust)
  - [How to use the CPU load-testing kit (blog)](https://db-blog.web.cern.ch/node/189)
- Metrics collection for Apache Spark performance troubleshooting: [sparkMeasure](https://github.com/LucaCanali/sparkMeasure)
- [Active benchmarking](https://www.brendangregg.com/activebenchmarking.html)
- A short list of [OS monitoring tools](https://github.com/LucaCanali/Miscellaneous/blob/master/Performance_Testing/Tools_Linux_OS_CPU_Disk_Network.md)

## Conclusions

This note presents an exploration of load methodologies using Apache Spark and a custom CPU and memory-intensive testing toolkit. 
The focus is on comparing different JDKs and producing insights into their respective performance when running Apache Spark jobs under specific conditions 
(CPU and memory-intensive load when reading Parquet files). 
While the results are limited to the stress test toolkit and the test environment, they illuminate the impact of JDK choices on CPU and memory-intensive workloads. 
The study underscores the significance of tailored testing and quantitative instrumentation practices, such as instrumenting Spark with metrics 
measurements using [sparkMeasure](https://github.com/LucaCanali/sparkMeasure), for deriving meaningful performance insights, and the importance of active
benchmarking methodologies for understanding the performance of the system under test. Active benchmarking implies measuring the system under load testing
with multiple tools and feed the measurements through an analysis process to understand the workload and sanity check against possible workload runtime errors and issues.
The results show that the JDK choice can have a significant impact on the performance of the CPU-intensive workload used for these tests, 
with the older Java 8 being the slowest, and GraalVM Java 17 being the fastest, with a ~25% improvement over Java 8, likely due to its improved JIT.

## Acknowledgements
I would like to express my sincere gratitude to my colleagues at CERN for their invaluable assistance and insightful suggestions,
in particular I'd like to acknowledge the CERN data analytics and web notebook services, and the ATLAS database and data engineering teams. 
