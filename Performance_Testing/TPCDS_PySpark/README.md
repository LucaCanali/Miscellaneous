# TPCDS_PySpark - Powering your Apache Spark Performance Lab.  
TPCDS_PySpark is a TPC-DS workload generator written in Python and designed to run at scale using Apache Spark. 
TPCDS_PySpark collects and reports performance metrics by integrating [sparkMeasure](https://github.com/LucaCanali/sparkMeasure),
a performance monitoring library for Apache Spark.  

## Motivations and goals
- TPCDS_PySpark provides tooling for investigating Spark performance. It is designed to be used for: 
  - Running TPC-DS workloads at scale and study Spark performance
  - Learning about collecting and analyzing Spark performance data, including timing and metrics measurements
  - Learning about Spark performance and optimization
  - Comparing performance across different Spark configurations and system configurations
  - It is written in Python, to ease the use and integration with Python notebooks and other Python-based tools

Author and contact: Luca.Canali@cern.ch   

### Contents
- [Key Features and benefits](#key-features-and-benefits)
- Getting started and examples
  - [Getting started - start small and scale up](#getting-started---start-small-and-scale-up)
  - [TPCDS at scale 10000G and analysis](#tpcds-at-scale-10000g-and-analysis)
- Operational instructions 
  - [Installation](#installation)
  - [One tool, two modes of operation](#one-tool-two-modes-of-operation)
  - [1. How to run TPCDS PySpark as a standalone script](#1-how-to-run-tpcds-pyspark-as-a-standalone-script)
  - [2. How to use TPCDS PySpark from your Python code](#2-how-to-use-tpcds-pyspark-from-your-python-code)
- [Advanced configurations and notes](#advanced-configurations-and-notes)
  - [Notes on TPC-DS schema and queries](#notes-on-tpc-ds-schema-and-queries)
  - [Notes on Spark Metrics Instrumentation](#notes-on-spark-metrics-instrumentation)
- Data generation and download
  - [Download TPCDS Data](#download-tpcds-data)
  - [Generate TPCDS data with a configurable scale factor](#generate-tpcds-data-with-a-configurable-scale-factor)
- [TPCDS_PySpark output](#tpcds_pyspark-output)
  - [Example output, TPCDS scale 10000 G](#example-output-tpcds-scale-10000-g)
- [Links and references](#links-and-references)

### Key Features and benefits

- **Comprehensive Benchmarking:** Execute the full suite of TPC-DS queries, in local mode or at scale on your Spark cluster(s)
  - Use this to evaluate how new clusters and Spark versions will perform before deploying in production.
  - Identify optimal Spark configurations (executor memory, parallelism, etc.)
- **Skill Development:** Deepen your understanding of Spark internals and best practices for high-performance distributed computing.
  - Use it to build a Performance Lab: a practical environment to experiment with Spark concepts.  
  - Experiment with [Spark task metrics](https://spark.apache.org/docs/latest/monitoring.html#executor-task-metrics) by using the integrated [sparkMeasure](https://github.com/LucaCanali/sparkMeasure) library to gather fine-grained performance metrics
(execution time, task metrics, etc.).  
  - Use it to experiment with other monitoring tools, such as: the [Spark Web UI](https://spark.apache.org/docs/latest/web-ui.html) and the [Spark-Dashboard](https://github.com/cerndb/spark-dashboard)  view of performance.

## Getting started - start small and scale up
You can start using TPCDS_PySpark by running the tool as a standalone Python script, from the command line, or by using it on a shared notebook service, like Colab.
TPCDS_PySpark runs on your laptop and/or shared notebook with minimal resources, while it can also scale up to run TPCDS on a large Spark cluster.  

**Python script: [download getstarted.py](Labs_and_Notes/getstarted.py)**  
  
**Notebooks:**  
**[<img src="https://raw.githubusercontent.com/googlecolab/open_in_colab/master/images/icon128.png" height="50"> Run TPCDS_PySpark get-started on Colab](https://colab.research.google.com/github/LucaCanali/Miscellaneous/blob/master/Performance_Testing/TPCDS_PySpark/Labs_and_Notes/TPCDS_PySpark_getstarted.ipynb)**    
**[<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/250px-Jupyter_logo.svg.png" height="50"> TPCDS_PySpark get-started](Labs_and_Notes/TPCDS_PySpark_getstarted.ipynb)**  

CERN users: **[![SWAN](https://swan.web.cern.ch/sites/swan.web.cern.ch/files/pictures/open_in_swan.svg) TPCDS_PySpark CERN-SWAN getstarted ](https://cern.ch/swanserver/cgi-bin/go?projurl=https://github.com/cerndb/SparkTraining.git)**


**Command line:**
```
# Get the tool
pip install tpcds_pyspark 

# Download the test data
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/tpcds_10.zip
unzip -q tpcds_10.zip

# 1. Run the tool for a minimal test
tpcds_pyspark_run.py -d tpcds_10 -n 1 -r 1 --queries q1,q2

# 2. run all queries with default options
tpcds_pyspark_run.py -d tpcds_10 

# 3. Scale CPU up, by running all queries on a YARN cluster and save the metrics to a file
TPCDS_PYSPARK=`which tpcds_pyspark_run.py`
spark-submit --master yarn --conf spark.log.level=error  --conf spark.executor.cores=8 \
             --conf spark.executor.memory=32g --conf spark.driver.memory=4g \
             --conf spark.driver.extraClassPath=tpcds_pyspark/spark-measure_2.12-0.24.jar \ 
             --conf spark.dynamicAllocation.enabled=false --conf spark.executor.instances=4 \
              $TPCDS_PYSPARK -d <HDFS_PATH>/tpcds_10 -o ./tpcds_10_out.cvs

# 4. Scale data up with TPCDS scale 100G
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/tpcds_100.zip
```

**TPCDS_PySpark in API mode:**

```
# Get the tool
pip install tpcds_pyspark 

# Download the test data
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/tpcds_10.zip
unzip -q tpcds_10.zip

$ python

from tpcds_pyspark import TPCDS

tpcds = TPCDS(num_runs=1, queries_repeat_times=1, queries=['q1','q2'])
tpcds.map_tables()

tpcds.run_TPCDS()
tpcds.print_test_results()
```

## TPCDS at scale 10000G and analysis  
This notebook demonstrates how to run TPCDS at scale 10000G and analyze the resulting performance metrics.
You will find analysis with graphs of the key metrics, such as query execution time, CPU usage, average active tasks, and more.

**[<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/250px-Jupyter_logo.svg.png" height="50"> TPCDS 10000G performance metrics analysis](Labs_and_Notes/TPCDS_analysis_scale_10000G.ipynb)**

---
## Installation:
A few steps to set up your Python environment for testing with TPCDS_PySpark:
```
python3 -m venv tpcds
source tpcds/bin/activate

pip install tpcds_pyspark
pip install pyspark
pip install sparkmeasure
pip install pandas
```

----

## One tool, two modes of operation:
- **Script mode**: run the tool as a standalone Python script, from the command line. Example:
  - `./tpcds_pyspark_run.py`
- **API mode:** use the tool as a library from your Python code.

### 1. How to run TPCDS PySpark as a standalone script:
```
tpcds_pyspark_run.py --help

options:
  -h, --help            show this help message and exit
  --data_path DATA_PATH, -d DATA_PATH
                        Path to the data folder with TPCDS data used for testing. Default: tpcds_10
  --data_format DATA_FORMAT
                        Data format of the data used for testing. Default: parquet
  --num_runs NUM_RUNS, -n NUM_RUNS
                        Number of runs, the TPCS workload will be run this number of times. Default: 2
  --queries_repeat_times QUERIES_REPEAT_TIMES, -r QUERIES_REPEAT_TIMES
                        Number of repetitions, each query will be run this number of times for each run. Default: 3
  --sleep_time SLEEP_TIME, -s SLEEP_TIME
                        Time in seconds to sleep before each query execution. Default: 1
  --queries QUERIES, -q QUERIES
                        List of TPCDS queries to run. Default: all
  --queries_exclude QUERIES_EXCLUDE, -x QUERIES_EXCLUDE
                        List of queries to exclude from the running loop. Default: None
  --output_file OUTPUT_FILE, -o OUTPUT_FILE
                        Optional output file, this will contain the collected metrics details in csv format
  --cluster_output_file CLUSTER_OUTPUT_FILE, -c CLUSTER_OUTPUT_FILE
                        Optional, save the collected metrics to a csv file using Spark, use this to save to HDFS or S3
  --run_using_metastore
                        Run TPCDS using tables defined in metastore tables instead of temporary views. See also --create_metastore_tables to define the tables.
                        Default: False
  --create_metastore_tables
                        Create metastore tables instead of using temporary views. Default: False
  --create_metastore_tables_and_compute_statistics
                        Create metastore tables and compute table statistics to use with Spark CBO. Default: False
```

### Examples:
- Run the tool for a minimal test  
  `./tpcds_pyspark_run.py -d tpcds_10 -n 1 -r 1 --queries q1,q2
- Run all queries with default options  
  `./tpcds_pyspark_run.py -d tpcds_10` 
- Run all queries on a YARN cluster and save the metrics to a file  
  ```
  spark-submit --master yarn --conf spark.log.level=error  --conf spark.executor.cores=8 \
               --conf spark.executor.memory=32g --conf spark.driver.memory=4g \
               --conf spark.driver.extraClassPath=tpcds_pyspark/spark-measure_2.12-0.24.jar \ 
               --conf spark.dynamicAllocation.enabled=false --conf spark.executor.instances=4 \
               tpcds_pyspark_run.py -d tpcds_10 -o ./tpcds_10_out.cvs -n 1 -r 1 
   ```
  
### 2. How to use TPCDS PySpark from your Python code 
- Use the TPCDS class to run TPCDS workloads from your Python code:
  - `pip install tpcds_pyspark`
  - `from tpcds_pyspark import TPCDS`

**API description: TPCDS**
- **TPCDS(data_path, data_format, num_runs=2, queries_repeat_times, queries, sleep_time)**
  - Defaults: data_path="./tpcds_10", data_format="parquet", num_runs=2, queries_repeat_times=3,
              queries=tpcds_queries, queries_exclude=[], sleep_time=1
- data_path: path to the Parquet folder with TPCDS data used for testing
- data_format: format of the TPCDS data, default: "parquet"
- num_runs: number of runs, the TPCS workload will be run this number of times. Default: 2
- queries_repeat_times: number of repetitions, each query will be run this number of times for each run. Default: 3
- queries: list of TPCDS queries to run
- queries_exclude: list of queries to exclude from the running loop
- sleep_time: time in seconds to sleep before each query execution. Default: 1
- Example: tpcds = TPCDS(data_path="tpcds_10", queries=['q1', 'q2'])

**TPCDS main class methods:**
- **map_tables:** map the TPCDS tables to the Spark catalog
  - map_tables(self, define_temporary_views=True, define_catalog_tables=False): 
  - this is a required step before running the TPCDS workload
  - Example: tpcds.map_tables()
- **run_TPCDS:** run the TPCDS workload
  - as side effect it populates the following class attributes: self.metadata, self.grouped, self.aggregated
  - Example: results = tpcds.run_TPCDS() 
- print_test_results(output_file=None): print the collected and aggregated metrics to stdout or to a file on the local filesystem
    containing the metadata, metrics grouped by query name and agregated metrics
- save_with_spark: save the collected metrics to a cluster filesystem (HDFS, S3) using Spark
  - save_with_spark(file_path): 
  - Example: tpcds.save_with_spark("HDFS_or_S3_path/my_test_metrics.csv") 
- compute_table_statistics: compute table statistics for the TPCDS tables (optional)
  - compute_table_statistics(collect_column_statistics=True)
  - use only when mapping tables to the Spark catalog (metastore) and when the statistics are not available
  - Example: tpcds.compute_table_statistics()


### Advanced configurations and notes

**Test with Spark on K8S and data on S3**
```
# Path to the tpcds_pyspark_run.py script
TPCDS_PYSPARK=`which tpcds_pyspark_run.py`

spark-submit --master k8s://https://..... --conf spark.kubernetes.container.image=..../myregistry/spark:v3.5.1 \
--conf spark.task.maxDirectResultSize=2000000000 --conf spark.shuffle.service.enabled=false --conf spark.executor.cores=8 \
--conf spark.executor.memory=64g --conf spark.driver.memory=16g --conf spark.driver.extraClassPath=tpcds_pyspark/spark-measure_2.12-0.24.jar \
--conf spark.executor.instances=4 --packages org.apache.hadoop:hadoop-aws:3.3.4 \
--conf spark.hadoop.fs.s3a.secret.key=$SECRET_KEY \
--conf spark.hadoop.fs.s3a.access.key=$ACCESS_KEY \
--conf spark.hadoop.fs.s3a.endpoint="https://s3.cern.ch" \
--conf spark.hadoop.fs.s3a.impl="org.apache.hadoop.fs.s3a.S3AFileSystem" \
--conf spark.executor.metrics.fileSystemSchemes="file,hdfs,s3a" \
--conf spark.hadoop.fs.s3a.fast.upload=true \
--conf spark.hadoop.fs.s3a.path.style.access=true \
--conf spark.hadoop.fs.s3a.list.version=1 \
$TPCDS_PYSPARK -d s3a://luca/tpcds_100 -o ./tpcds_pyspark_K8S_S3A_tpcds100.csv 
```

**Test with CBO on YARN at scale**
```
# Path to the tpcds_pyspark_run.py script
TPCDS_PYSPARK=`which tpcds_pyspark_run.py`

# Map tables to the Spark catalog
spark-submit --master yarn --conf spark.log.level=error  --conf spark.executor.cores=8 --conf spark.executor.memory=64g \
--conf spark.driver.memory=16g --conf spark.driver.extraClassPath=tpcds_pyspark/spark-measure_2.12-0.24.jar \
--conf spark.executor.instances=32 --conf spark.sql.shuffle.partitions=512 --conf spark.sql.catalogImplementation=hive \
 $TPCDS_PYSPARK -d /project/spark/TPCDS/tpcds_10000_parquet_1.13.1  --create_metastore_tables_and_compute_statistics

# test with metastore statistics
spark-submit --master yarn --conf spark.log.level=error  --conf spark.executor.cores=8 --conf spark.executor.memory=64g \
--conf spark.driver.memory=16g --conf spark.driver.extraClassPath=tpcds_pyspark/spark-measure_2.12-0.24.jar \
--conf spark.executor.instances=32 --conf spark.sql.shuffle.partitions=512 --conf spark.sql.catalogImplementation=hive \
--conf spark.sql.cbo.enabled=true \
$TPCDS_PYSPARK -d /project/spark/TPCDS/tpcds_10000_parquet_1.13.1 --run_using_metastore -o ./tpcds_pyspark_YARN_CBO_.csv
```

### Notes on TPC-DS schema and queries
- [Labs_and_Notes/TPCDS_schema.md](TPCDS_schema.md) contains a description of the TPCDS schema used by TPCDS_PySpark, with a list of the tables and details of their columns and data types
- [Labs_and_Notes/TPCDS_queries](TPCDS_queries) contains a description of selected TPCDS queries used by TPCDS_PySpark, with a list of the queries and their SQL code

### Notes on Spark Metrics Instrumentation
Spark is instrumented with several metrics, collected at task execution, they are described in the documentation:  
- [Spark Task Metrics docs](https://spark.apache.org/docs/latest/monitoring.html#executor-task-metrics)

Some of the key metrics when looking at a sparkMeasure report are:
- **elapsedTime:** the time taken by the stage or task to complete (in millisec)
- **executorRunTime:** the time the executors spent running the task, (in millisec). Note this time is cumulative across all tasks executed by the executor.
- **executorCpuTime:** the time the executors spent running the task, (in millisec). Note this time is cumulative across all tasks executed by the executor.
- **jvmGCTime:** the time the executors spent in garbage collection, (in millisec).
- shuffle metrics: several metrics with details on the I/O and time spend on shuffle
- I/O metrics: details on the I/O throughput (for reads and writes). Note, currently there are no time-based metrics for I/O operations.

- Comparing metrics:
  - When computing `executorRunTime - (executorCpuTime + jvmGCTime + other time-based metrics)`, what we obtain is roughly the "uninstrumented time".
    For TPCDS queries this is mostly I/O time. In general this instrumented time could have other origin, including running Python UDF or, more generally,
    time spent "outside Spark"
  - `executorRunTime / elapsedTime` is a rough measure of the CPU utilization of the task. This is a useful metric to understand how much of the elapsed time is spent in CPU-bound operations.

---
## Download TPCDS Data
The tool requires TPCDS benchmark data in parquet or other format. 
For convenience the TPCDS benchmark data at scale 10G and 100G have been made available for downloading:
```
# Get TPCDS data at scale 10G
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/tpcds_10.zip
unzip -q tpcds_10.zip

# Get TPCDS data at scale 100G
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/tpcds_100.zip
unzip tpcds_100.zip
```

## Generate TPCDS data with a configurable scale factor

- You can generate Spark TPCDS benchmark data at any scale using the following steps:
  - Download and build the Spark package from https://github.com/databricks/spark-sql-perf
  - Download and build tpcds-kit for generating data from https://github.com/databricks/tpcds-kit

See instructions at the [spark-sql-perf](https://github.com/databricks/spark-sql-perf) for additional info here some pointers/examples:
```
// 1. Generate schema
bin/spark-shell --master yarn --num-executors 25 --driver-memory 12g --executor-memory 12g --executor-cores 4 --jars <path_here>/spark-sql-perf_2.12-0.5.1-SNAPSHOT.jar

NOTES:
  - Each executor will spawn dsdgen to create data, using the parameters for size (e.g. 10000) and number of partitions (e.g. 1000)
  - Example: bash -c cd /home/luca/tpcds-kit/tools && ./dsdgen -table catalog_sales -filter Y -scale 10000 -RNGSEED 100 -parallel 1000 -child 107
  - Each "core" in the executor spawns one dsdgen
  - This workloads is memory hungry, to avoid excessive GC activity, allocate abundant memory per executor core

// Use this to generate partitioned data: scale 10000G partitioned
val tables = new com.databricks.spark.sql.perf.tpcds.TPCDSTables(spark.sqlContext, "/home/luca/tpcds-kit/tools", "10000")
tables.genData("/user/luca/TPCDS/tpcds_10000", "parquet", true, true, true, false, "", 100)

// Use this instead to generate a smaller dataset for testing and development, non-partitioned: scale 10G non-partitioned
val tables = new com.databricks.spark.sql.perf.tpcds.TPCDSTables(spark.sqlContext, "/home/luca/tpcds-kit/tools", "10")
tables.genData("/user/luca/TPCDS/tpcds_10_non_partiitoned", "parquet", true, false, false, false, "", 10)
```

You can also use the following code to copy TPCDS data and potentially convert it in a different format or compression algorithm:
```
bin/spark-shell --master yarn --driver-memory 4g --executor-memory 64g --executor-cores 8 --conf spark.sql.shuffle.partitions=400

val inpath="/project/spark/TPCDS/tpcds_10000_parquet_1.13.1/"
val format="orc"
val compression_type="zstd"
val outpath="/user/luca/TPCDS/tpcds_10000_orc_1.9.1/"

val tables_partition=List(("catalog_returns","cr_returned_date_sk"), ("catalog_sales","cs_sold_date_sk"), ("inventory","inv_date_sk"), ("store_returns","sr_returned_date_sk"), ("store_sales","ss_sold_date_sk"), ("web_returns","wr_returned_date_sk"), ("web_sales","ws_sold_date_sk"))
for (t <- tables_partition) {
  println(s"Copying partitioned table $t")
  spark.read.parquet(inpath + t._1).repartition(col(t._2)).write.partitionBy(t._2).mode("overwrite").option("compression", compression_type).format(format).save(outpath + t._1)
}

val tables_nopartition=List("call_center","catalog_page","customer","customer_address","customer_demographics","date_dim","household_demographics","income_band","item","promotion","reason","ship_mode","store","time_dim","warehouse","web_page","web_site")
for (t <- tables_nopartition) {
  println(s"Copying table $t")
  spark.read.parquet(inpath + t).coalesce(1).write.mode("overwrite").option("compression", compression_type).format(format).save(outpath + t)
}
```

----
## TPCDS_PySpark output
- TPCDS_PySpark print to stdout the collected metrics, including timing and metrics measurements.
  - It will also print metadata, metrics grouped by query name, and aggregated metrics
  - You can save the collected metrics to a local csv files: `-o my_test_metrics.csv`
  - Optionally, save the collected metrics to a cluster filesystem (HDFS, S3) using Spark: `--cluster_output_file PATH/my_test_metrics.csv` 

There are 4 files in the output:
  - raw metrics: this contains the timestamp, elapsed time, and metrics for each query execution, including repeated executions of the same query
  - grouped metrics: this contains the metrics grouped by query name. For each query the median values of the metrics are reported
  - aggregated metrics: this contains the aggregated metrics for the entire workload, including the total elapsed time, executor run time, CPU time, and more
  - metadata: this contains the metadata of the test, including the configuration and the start and end times of the test

## Example output, TPCDS scale 10000 G:
```
****************************************************************************************
TPCDS with PySpark - workload configuration and metadata summary
****************************************************************************************

Queries list = q1, q2, q3, q4, q5, q5a, q6, q7, q8, q9, q10, q10a, q11, q12, q13, q14a, q14b, q14, q15, q16, q17, q18, q18a, q19, q20, q21, q22, q22a, q23a, q23b, q24, q24a, q24b,
q25, q26, q27, q27a, q28, q29, q30, q31, q32, q33, q34, q35, q35a, q36, q36a, q37, q38, q39a, q39b, q40, q41, q42, q43, q44, q45, q46, q47, q48, q49, q50, q51, q51a, q52, q53, q54,
 q55, q56, q57, q58, q59, q60, q61, q62, q63, q64, q65, q66, q67, q67a, q68, q69, q70, q70a, q71, q72, q73, q74, q75, q76, q77, q77a, q78, q79, q80, q80a, q81, q82, q83, q84, q85,
q86, q86a, q87, q88, q89, q90, q91, q92, q93, q94, q95, q96, q97, q98, q99
Number of runs = 2
Query execution repeat times = 3
Total number of executed queries = 708
Sleep time (sec) between queries = 1
Queries path = /home/luca/python/lib/python3.11/site-packages/tpcds_pyspark/Queries
Data path = hdfs://analytix/project/spark/TPCDS/tpcds_10000_parquet_1.13.1
Start time = Fri Mar  8 22:17:48 2024
End time = Sat Mar  9 12:26:43 2024

Spark version = 3.5.1
Spark master = yarn
Executor memory: 64g
Executor cores: 8
Dynamic allocation: false
Number of executors: 32
Cost Based Optimization (CBO): false
Histogram statistics: false

****************************************************************************************
Queries execution metrics - grouped
****************************************************************************************
query,numStages,numTasks,elapsedTime,stageDuration,executorRunTime,executorCpuTime,executorDeserializeTime,executorDeserializeCpuTime,resultSerializationTime,jvmGCTime,shuffleFetch
WaitTime,shuffleWriteTime,resultSize,diskBytesSpilled,memoryBytesSpilled,peakExecutionMemory,recordsRead,bytesRead,recordsWritten,bytesWritten,shuffleRecordsRead,shuffleTotalBlocks
Fetched,shuffleLocalBlocksFetched,shuffleRemoteBlocksFetched,shuffleTotalBytesRead,shuffleLocalBytesRead,shuffleRemoteBytesRead,shuffleRemoteBytesReadToDisk,shuffleBytesWritten,shu
ffleRecordsWritten,avg_active_tasks,elapsed_time_seconds
q1,12,1735,16403,27174,1126023,892056,21929,7776,92,15123,420,5780,5644249,0,0,309889451952,1181741562,10916205123,0,0,545966999,205065,12456,192609,4978913160,398729640,4580186764
,0,4980068218,546002039,68,16
q2,14,25594,37221,58900,4836401,3182779,83667,85379,195,67767,0,204,99956814,0,0,374837827752,43052456356,172941221672,0,0,11630,8213,221,7992,318903,23697,295206,0,212509,8451,129
,37
q3,5,1750,7526,7425,431925,197063,8603,4842,21,2999,0,1385,10551205,0,0,118053926672,4411258078,35209694631,0,0,389702,37770,1437,36333,23387274,876217,22511056,0,23387274,389702,5
7,7
q4,23,15206,195419,1113439,47973436,42672736,51141,33751,150,330677,68012,300958,16581895,0,0,5247548963256,19607435671,311247671699,0,0,20397726323,6755226,233094,6521145,32205227
0765,11340295539,310711986663,0,306951146835,20072726323,245,195
q5,11,5886,93585,114301,15944752,14865948,19594,11072,42,20001,9402,64563,10449459,0,0,1270759090008,7757286572,48055907550,0,0,7203625949,2112366,78370,2033996,66782312822,2472085
512,64310227205,0,66782312822,7203625949,170,93
q5a,14,5777,93187,113880,15524927,14750847,18694,10888,38,20453,7771,63686,10453178,0,0,1270347392528,7752093222,47965384648,0,0,7200662968,2112387,78544,2033842,66737665741,247851
9722,64259145754,0,66737093032,7200655470,166,93
q6,12,1424,14914,27923,394816,376462,4433,3532,4,1076,604,3366,8222634,0,0,230050649076,419235746,2444876874,0,0,475794219,197522,98661,98860,2275391383,859592243,1415799259,0,2275
391383,475794219,26,14
...
...
q95,14,9785,168695,218500,30846694,26885346,44501,36217,60,346361,1173,27735,10442557,0,0,2657047902600,15152577041,103172868876,0,0,29635061602,9153184,306824,8846360,40122805555,
1339492316,38783313197,0,13435493752,8040409045,182,168
q96,5,11203,28810,28775,2493048,1655637,15216,15447,64,11162,0,4974,26162863,0,0,1347553272,28799984813,92770940311,0,0,11199,11199,74,11125,358368,2368,356000,0,358368,11199,86,28
q97,5,4439,82114,107300,16391402,15742453,18267,10681,30,28974,64,54421,11502095,0,0,2648891819296,8396730903,45954612966,0,0,8281164253,2010112,69408,1940704,63030776309,218753935
0,60843236959,0,63030776309,8281164253,199,82
q98,8,649,15279,16957,284556,263390,2747,1664,27,960,842,1618,12941559,0,0,112026213184,261571517,2110123219,0,0,261510330,44820,7488,37331,1663227592,251015398,1412212573,0,165828
3366,261450176,18,15
q99,7,9012,30581,30423,3210151,2176471,31288,25786,22,10979,5704,5881,58715017,0,0,354528117664,14399900462,38235996543,0,0,10025697,713376,24265,689110,447115058,15271221,43184383
6,0,447115058,10025697,104,30

****************************************************************************************
Queries execution metrics - aggregated
****************************************************************************************
Metric_name,Value
numStages,8576
numTasks,5611656
elapsedTime,50020340
stageDuration,89015663
executorRunTime,7249768525
executorCpuTime,6143253253
executorDeserializeTime,20628045
executorDeserializeCpuTime,13372460
resultSerializationTime,42840
jvmGCTime,41301806
shuffleFetchWaitTime,7975952
shuffleWriteTime,40766753
resultSize,11999438913
diskBytesSpilled,4323320343608
memoryBytesSpilled,14937648562784
recordsRead,10794916497774
bytesRead,71000603668818
recordsWritten,0
bytesWritten,0
shuffleRecordsRead,3953004648186
shuffleTotalBlocksFetched,1573646698
shuffleLocalBlocksFetched,65488533
shuffleRemoteBlocksFetched,1508158165
shuffleTotalBytesRead,30260277830892
shuffleLocalBytesRead,1243171382982
shuffleRemoteBytesRead,29017106447910
shuffleRemoteBytesReadToDisk,0
shuffleBytesWritten,23622972934884
shuffleRecordsWritten,2880682284700
avg_active_tasks,144
elapsed_time_seconds,50020
```

---
## Links and references

- [TPCDS-PySpark on Pypi](https://pypi.org/project/TPCDS-PySpark)
- TPCDS official website: [TPCDS](http://www.tpc.org/tpcds/)
- TPCDS queries: [TPCDS from Apache Spark tests](https://github.com/apache/spark/tree/master/sql/core/src/test/resources/tpcds)
and [TPCDS-v2.7.0 from Apache Spark tests](https://github.com/apache/spark/tree/master/sql/core/src/test/resources/tpcds-v2.7.0)
- See also [Databricks' spark-sql-perf](https://github.com/databricks/spark-sql-perf)
- [IBM TPCDS on Spark](https://github.com/IBM/spark-tpc-ds-performance-test)
- TPCDS schema creation from: [TPCDS Kit](https://github.com/databricks/tpcds-kit)
- [sparkMeasure](https://github.com/LucaCanali/sparkMeasure)
- [Performance Troubleshooting Using Apache Spark Metrics](http://canali.web.cern.ch/docs/Spark_Performance_Troubleshooting_Metrics_SAISEU2019_Luca_Canali_CERN.pdf)
  Spark Summit Europe 2019
