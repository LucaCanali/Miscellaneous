# CPU and memory-intensive load testing kit using Apache Spark
This folder contains code and examples of a tool designed for conducting CPU and CPU-to-memory bandwidth load testing.  
The workload is implemented using PySpark and is designed to be CPU- and memory-intensive.
It involves executing a Spark job that reads a large Parquet table in parallel, utilizing a user-defined number of parallel workers.  
The primary output of the tool is the measurement of the job execution time, which is recorded as a function of the number of parallel workers employed.  
Running the program in full mode initiates a range of tests and generates a CSV file that contains the recorded values.  
In addition to the code and examples, this folder also includes sample data collected with the tool and Jupyter notebooks used for data analysis purposes.  

## Contents
- [test_Spark_CPU_memory.py](test_Spark_CPU_memory.py) - a Python script to run the workload with Spark and measure job runtime and additional instrumentation.
- [spark-measure_2.12-0.23.jar](spark-measure_2.12-0.23.jar) - instrumentation library for Spark, from [sparkMeasure](https://github.com/LucaCanali/sparkMeasure)
- [Test_CPUs](Test_CPUs) How to use test_Spark_CPU_memory to measure CPU scalability.
- [Test_JDKs](Test_JDKs) Example of using test_Spark_CPU_memory to compare performance across different JDKs.

## How to use the tool 

### 1. Prepare the environment:
Install [PySpark](https://pypi.org/project/pyspark/) and [sparkMeasure's](https://github.com/LucaCanali/sparkMeasure) Python bindings
```
pip install pyspark
pip install sparkmeasure
```
Download/clone from the repo: `test_Spark_CPU_memory.py` and `spark-measure_2.12-0.23.jar`  

### 2. Download the test data used for load generation:   
- The tool uses a large the Parquet table, store_sales, taken from the open source TPCDS benchmark.
- You can generate the table data from the benchmark scripts or download from the following location:  
[store_sales](https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/store_sales.parquet/)    
- You can download data from the store_sales.parquet folder with the following command (note you will need 190 GB to store the full dataset):  
`wget -r -np -nH --cut-dirs=2 -R "index.html*" -e robots=off http://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/store_sales.parquet/`

- **Notes:** 
  - `test_Spark_CPU_memory.py` is originally intended to run on CPU and "in memory", so you will need to have enough memory to store the data and the
  Spark heap. This has been tested on a machine with 512 GB of RAM. If you have less memory, you can reduce the size of the dataset,
  by removing some of the files from the store_sales.parquet folder.
  - when starting tests with a large number of workers the tool can generate a significant load, use this tool rather on test systems.

### 3. Run [test_Spark_CPU_memory.py](test_Spark_CPU_memory.py):
```
Examples:
# run one-off data collection with 2 concurrent workers
./test_Spark_CPU_memory.py --num_workers 2

# Measure job runtime over a ramp of concurrent workers from 1 to 8, and output the results to a CSV file
./test_Spark_CPU_memory.py --num_workers 8 --full --output myout.csv 

Usage:

test_Spark_CPU_memory.py - A workload generator with Apache Spark, instrumented using sparkMeasure.
Luca.Canali@cern.ch - April 2023

Use this to generate CPU-intensive and memory-intensive load on a system.
The tool runs a PySpark job with concurrent activity by multiple tasks,
with configurable load.
Multiple runs are performed and the average execution time is reported.
The tool outputs measurements of the job execution time as a function of load,
as well as metrics from sparkMeasure, notably executor tasks run time, 
CPU time and Garbage collection time.
Use full mode to collect speedup measurements and create plots.

Example:
./test_Spark_CPU_memory.py --num_workers 2

Parameters:

--full - Full mode will test all the values of num_workers from 1 to the value 
         set with --num_workers, use this to collect speedup test measurements and create plots, default = False
--output - Optional output file, applies only to the full mode, default = None
--num_workers - Number of parallel threads running concurrently, default = 2
--num_job_execution_loops - number of times the execution loop is run on each worker, default = 3
--worker_inner_loop_size - internal weight of the inner execution loop, default = 100000000
--spark_heap_size - Spark heap size, default = 64g
--data_path - path to the parquet files used for testing, default = ./store_sales.parquet
--sparkmeasure_path - path to the sparkmeasure package, default = ./spark-measure_2.12-0.23.jar
```

### Motivations and limitations
- This tool serves the purpose of generating CPU and memory-intensive load on a system by executing multiple Spark tasks in parallel.
- It's primary objective is to measure the scalability of both CPU and memory bandwidth using the full mode and the accompanying analysis notebooks.
- It allows for a comparison of CPU and memory throughput scalability across different systems. However, it's important to note that for accurate
  comparisons, the same versions of Spark, Python, and glibc should be used, as these factors can influence the results.
- It is important to acknowledge that the measurements obtained with this tool may exhibit some noise, particularly when Garbage Collection interferes.
  To mitigate this, it is recommended to allocate substantial amounts of memory to the executors and carefully examine the tool's output for metrics
  such as GC time and CPU time.
- This tool is not designed as a benchmark. Instead, its primary function is to generate CPU and memory-intensive load and assess the scalability
  of CPU and memory on a given system.
- The key part of the tool is about scanning Parquet data, this works in Spark because:
  - `spark.sql.parquet.filterPushdown=false` forces Spark to read all the data from the Parquet files
  - [SPARK-42256](https://issues.apache.org/jira/browse/SPARK-42256) The current implementation of Spark requires the read values to materialize
    (i.e. de-compress, de-code, etc...) onto memory first before applying the filters.
- Note the store_sales table has been post processed using Spark as follows:
   ```
   val df = spark.read.parquet("PATH/store_sales")
   df.repartition(128,col("ss_sold_date_sk")).sortWithinPartitions("ss_sold_date_sk","ss_sold_time_sk","ss_customer_sk").write.parquet("PATH/store_sales.parquet")
   ```

## FlameGraph
Follow this link to a [FlameGraph of the execution profile](http://canali.web.cern.ch/svg/FlameGraph_test_Spark_CPU_memory.html) taken
during a run of [test_Spark_CPU_memory.py](test_Spark_CPU_memory.py) (see [Test_JDKs](Test_JDKs) for details).  
The FlameGraph shows that the workload is CPU-bound, and that the time is spent in the Spark SQL code, in particular in the Parquet reader.
FlameGraphs are a visualization tool for profiling the performance of applications, see also [Tools_FlameGraphs.md](../Tools_FlameGraphs.md).  

Contact: Luca.Canali@cern.ch
