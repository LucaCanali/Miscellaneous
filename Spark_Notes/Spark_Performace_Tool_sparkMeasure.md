# HowTo: Measure Spark Performance Metrics With sparkMeasure

This is a get-started doc to sparkMeasure: 
  * https://github.com/LucaCanali/sparkMeasure
  * https://mvnrepository.com/artifact/ch.cern.sparkmeasure

SparkMeasure is a tool for performance investigations of Apache Spark workloads.   
  * It helps with the collection and analysis of Spark workload **metrics**.
  * It can be used from the command line (**spark-shell, PySpark, or Notebooks**)
  * It can be used for instrumenting **applications**, see "flight recorder mode"
  * For Spark 2.1.x and higher

Try sparkMeasure out:

```
bin/spark-shell --packages ch.cern.sparkmeasure:spark-measure_2.11:0.11

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

More info and examples:
  * https://github.com/LucaCanali/sparkMeasure/blob/master/README.md
  * http://db-blog.web.cern.ch/blog/luca-canali/2017-03-measuring-apache-spark-workload-metrics-performance-troubleshooting
  