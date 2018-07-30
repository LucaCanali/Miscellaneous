# HowTo: Measure Spark Performance Metrics With sparkMeasure
This is a get-started doc to sparkMeasure.
  * https://github.com/LucaCanali/sparkMeasure
  * https://mvnrepository.com/artifact/ch.cern.sparkmeasure

SparkMeasure is a tool for performance investigations of Apache Spark workloads.   
  * It helps with the collection and analysis of Spark workload **metrics**.
  * It can be used from the command line (**spark-shell, PySpark, or Notebooks**)
  * It can be used for instrumenting **applications**, see "flight recorder mode"
  * For Spark 2.1.x and higher

   
Try sparkMeasure out on your local installation with a simple example   
Or see this [example Notebook on Databricks](https://databricks-prod-cloudfront.cloud.databricks.com/public/4027ec902e239c93eaaa8714f173bcfc/2061385495597958/2729765977711377/442806354506758/latest.html)


```
bin/spark-shell --packages ch.cern.sparkmeasure:spark-measure_2.11:0.13

val stageMetrics = ch.cern.sparkmeasure.StageMetrics(spark) 
stageMetrics.runAndMeasure(spark.sql("select count(*) from range(1000) cross join range(1000) cross join range(1000)").show)
```


The output should look like this:
```
Scheduling mode = FIFO
Spark Context default degree of parallelism = 8
Aggregated Spark stage metrics:
numStages => 3
sum(numTasks) => 17
elapsedTime => 9103 (9 s)
sum(stageDuration) => 9027 (9 s)
sum(executorRunTime) => 69238 (1.2 min)
sum(executorCpuTime) => 68004 (1.1 min)
sum(executorDeserializeTime) => 1031 (1 s)
sum(executorDeserializeCpuTime) => 151 (0.2 s)
sum(resultSerializationTime) => 5 (5 ms)
sum(jvmGCTime) => 64 (64 ms)
sum(shuffleFetchWaitTime) => 0 (0 ms)
sum(shuffleWriteTime) => 26 (26 ms)
max(resultSize) => 17934 (17.0 KB)
sum(numUpdatedBlockStatuses) => 0
sum(diskBytesSpilled) => 0 (0 Bytes)
sum(memoryBytesSpilled) => 0 (0 Bytes)
max(peakExecutionMemory) => 0
sum(recordsRead) => 2000
sum(bytesRead) => 0 (0 Bytes)
sum(recordsWritten) => 0
sum(bytesWritten) => 0 (0 Bytes)
sum(shuffleTotalBytesRead) => 472 (472 Bytes)
sum(shuffleTotalBlocksFetched) => 8
sum(shuffleLocalBlocksFetched) => 8
sum(shuffleRemoteBlocksFetched) => 0
sum(shuffleBytesWritten) => 472 (472 Bytes)
sum(shuffleRecordsWritten) => 8
```

**More info and examples:**
  * https://github.com/LucaCanali/sparkMeasure/blob/master/README.md
  * http://db-blog.web.cern.ch/blog/luca-canali/2017-03-measuring-apache-spark-workload-metrics-performance-troubleshooting
  * https://github.com/LucaCanali/sparkMeasure/blob/master/examples/SparkTaskMetricsAnalysisExample.ipynb
  * Another example using TPC-DS table store_sales from http://db-blog.web.cern.ch/blog/luca-canali/2017-06-diving-spark-and-parquet-workloads-example

```
val stageMetrics = ch.cern.sparkmeasure.StageMetrics(spark)
stageMetrics.runAndMeasure(spark.sql("select * from store_sales where ss_sales_price=-1").collect())

Scheduling mode = FIFO
Spark Context default degree of parallelism = 48
Aggregated Spark stage metrics:
numStages => 1
sum(numTasks) => 1675
elapsedTime => 75684 (1.3 min)
sum(stageDuration) => 75684 (1.3 min)
sum(executorRunTime) => 3525951 (59 min)
sum(executorCpuTime) => 1006093 (17 min)
sum(executorDeserializeTime) => 4410 (4 s)
sum(executorDeserializeCpuTime) => 2106 (2 s)
sum(resultSerializationTime) => 69 (69 ms)
sum(jvmGCTime) => 811933 (14 min)
sum(shuffleFetchWaitTime) => 0 (0 ms)
sum(shuffleWriteTime) => 0 (0 ms)
max(resultSize) => 2346124 (2.0 MB)
sum(numUpdatedBlockStatuses) => 48
sum(diskBytesSpilled) => 0 (0 Bytes)
sum(memoryBytesSpilled) => 0 (0 Bytes)
max(peakExecutionMemory) => 0
sum(recordsRead) => 4319943621
sum(bytesRead) => 198992404103 (185.0 GB)
sum(recordsWritten) => 0
sum(bytesWritten) => 0 (0 Bytes)
sum(shuffleTotalBytesRead) => 0 (0 Bytes)
sum(shuffleTotalBlocksFetched) => 0
sum(shuffleLocalBlocksFetched) => 0
sum(shuffleRemoteBlocksFetched) => 0
sum(shuffleBytesWritten) => 0 (0 Bytes)
sum(shuffleRecordsWritten) => 0


scala> stageMetrics.printAccumulables

Aggregated Spark accumulables of type internal.metric. Sum of values grouped by metric name
Name => sum(value) [group by name]

executorCpuTime => 1006093 (17 min)
executorDeserializeCpuTime => 2106 (2 s)
executorDeserializeTime => 4410 (4 s)
executorRunTime => 3525951 (59 min)
input.bytesRead => 198992404103 (185.0 GB)
input.recordsRead => 4319943621
jvmGCTime => 811933 (14 min)
resultSerializationTime => 69 (69 ms)
resultSize => 2346124 (2.0 MB)

SQL Metrics and other non-internal metrics. Values grouped per accumulatorId and metric name.
Accid, Name => max(value) [group by accId, name]

256, number of output rows => 4319943621
259, scan time total => 3327453 (55 min)
260, duration total => 3522020 (59 min)

```

