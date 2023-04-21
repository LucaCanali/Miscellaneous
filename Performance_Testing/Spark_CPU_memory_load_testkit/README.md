# Spark-based CPU and memory-intensive load testkit
This folder contains a Spark-based tool to load test CPUs and memory and measure job execution time as a function of the number of parallel workers.
The workload is implemented in Python using PySpark.
The workload is CPU and memory intensive and consists of a Spark job reading a large Parquet table in parallel.
The tool will produce as output the measurement of the job execution time as a function of the number of parallel workers.  
When run in full mode, the program will run a range of tests and output a cvs file with the measured values.
This folder contains also example Data collected with the tool and Jupyter notebooks used to analyze the data.

### Contents
- [test_Spark_CPU_memory_instrumented.py](test_Spark_CPU_memory_instrumented.py) Python script to run the worklod with Spark and measure job runtime and additional instrumentation.
- [spark-measure_2.12-0.23.jar](spark-measure_2.12-0.23.jar) this is the instrumentation library compiled from [sparkMeasure](https://github.com/LucaCanali/sparkMeasure)
- [Data](Data) contains example data collected with test_Spark_CPU_memory_instrumented.py
- [Memory_throughput](Memory_throughput) measurements of CPU-to-memory throughput measured while running test_Spark_CPU_memory_instrumented.py
- [Notebooks](Notebooks) contains Jupyter notebooks used to analyze the collected data.

### Motivations and limitations
- Use this to generate CPU and memory-intensive load on a system by running multiple Spark tasks in parallel.
- Measure the scalability of the CPU and memory bandwidth using full mode and the provided analysis notebooks
- Compare CPU and memory throughput scalability across systems
  - Note that when comparing different systems you want to use the same Spark, Python and glibc versions, as these can affect the results 
- Measurements with this tool can be noisy, in particular when Garbage Collection gets in the way, for this allocate large amounts
  of memory to the executors and examine the tool output for the measured metrics of GC time and CPU time. 
- This is not a benchmark but rather a tool to generate CPU and memory-intensive load and measure the scalability of the CPU+memory on a system

### How to prepare the environment:
Python:
```
pip install pyspark
pip install sparkmeasure
```
Test data: 
Prepare the data used by the tool, the Parquet table store_sales from the TPCDS demo.
A version of the table is available for download at:
[store_sales](https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/store_sales.parquet/)    
You can download the full store_sales.parquet folder with the following command:  
`wget -r -np -nH --cut-dirs=2 -R "index.html*" -e robots=off http://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/store_sales.parquet/`

Note the table has been post processed using Spark as follows:
```
val df = spark.read.parquet("PATH/store_sales")
df.repartition(128,col("ss_sold_date_sk")).sortWithinPartitions("ss_sold_date_sk","ss_sold_time_sk","ss_customer_sk").write.parquet("PATH/store_sales.parquet")
```

### How to use [test_Spark_CPU_memory_sparkmeasure.py](test_Spark_CPU_memory_sparkmeasure.py):
```
test_Spark_CPU_memory_sparkmeasure.py - A workload generator with Apache Spark, instrumented using sparkMeasure.
Luca.Canali@cern.ch - April 2023

Use this to generate CPU-intensive and memory-intensive load on a system.
The tool runs a PySpark job with concurrent activity by multiple tasks,
with configurable load.
Multiple runs are performed and the average execution time is reported.
The tool outputs measurements of the job execution time as function of load,
as well as metrics from sparkMeasure, notably executor tasks run time, 
CPU time and Garbage collection time.
Use full mode to collect speedup measurements and create plots.

Example:
./test_Spark_CPU_memory_sparkmeasure.py --num_workers 2

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
"""
