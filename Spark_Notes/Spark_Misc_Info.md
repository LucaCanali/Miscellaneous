# Spark Miscellaneous
Info, commands and tips

- turn off dynamic allocation   
`--conf spark.dynamicAllocation.enabled=false`
- Hadoop native library for short-circuit reads (should be configured at system level otherwise)  
`--conf spark.executor.extraLibraryPath=/usr/lib/hadoop/lib/native`
- Example command line for spark-shell/pyspark/spark-submit  
`--master yarn --num-executors 5 --executor-cores 4 --executor-memory 7g --driver-memory 7g`
- Workload profile with [sparkMeasure](Spark_Performace_Tool_sparkMeasure.md)   
```
bin/spark-shell --packages ch.cern.sparkmeasure:spark-measure_2.11:0.11
val stageMetrics = ch.cern.sparkmeasure.StageMetrics(spark) 
stageMetrics.runAndMeasure(spark.sql("select count(*) from range(1000) cross join range(1000)").show)
```
- Read and set configuration variables from Hadoop  
```
sc.hadoopConfiguration.get("dfs.blocksize")
sc.hadoopConfiguration.getValByRegex(".").toString.split(", ").sorted.foreach(println)
sc.hadoopConfiguration.setInt("parquet.block.size", 256*1024*1024)
```
- Specify JAVA_HOME to use in a YARN cluster   
`bin/spark-shell --conf spark.yarn.appMasterEnv.JAVA_HOME=/usr/lib/jvm/java-oracle --conf spark.executorEnv.JAVA_HOME=/usr/lib/jvm/java-oracle`

