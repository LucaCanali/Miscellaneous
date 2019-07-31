## Spark Miscellaneous - Info, commands and tips

- Workload profile with [sparkMeasure](Spark_Performace_Tool_sparkMeasure.md)   
```
bin/spark-shell --packages ch.cern.sparkmeasure:spark-measure_2.11:0.11
val stageMetrics = ch.cern.sparkmeasure.StageMetrics(spark) 
stageMetrics.runAndMeasure(spark.sql("select count(*) from range(1000) cross join range(1000)").show)
```
---
- Allocate Spark Session from API
```
// Scala
import org.apache.spark.sql._
val spark = SparkSession.
    builder().
    appName("my app").
    master("local[*]").   // use master("yarn") for a YARN cluster
    config("spark.driver.memory","2g").  // set all the parameters as needed
    getOrCreate() 

# Python
from pyspark.sql import SparkSession
spark = SparkSession.builder \
        .appName("my app")  \
        .master("yarn") \
        .config("spark.driver.memory","8g") \
        .config("spark.executor.memory","14g") \
        .config("spark.executor.cores","4") \
        .config("spark.executor.instances","8") \
        .config("spark.dynamicAllocation.enables","false") \
        .getOrCreate()
```
---
- Spark commit and PRs, see what's new
  - Spark commits to master: https://github.com/apache/spark/commits/master
  - Spark PRs: https://spark-prs.appspot.com/
  - Documentation: 
     - https://github.com/apache/spark/tree/master/docs 
     - https://spark.apache.org/docs/latest/
     - SQL grammar https://github.com/apache/spark/blob/master/sql/catalyst/src/main/antlr4/org/apache/spark/sql/catalyst/parser/SqlBase.g4
     - https://docs.databricks.com/index.html 

---
- How to build Spark
  - see also https://spark.apache.org/docs/latest/building-spark.html
```
git clone https://github.com/apache/spark.git
cd spark
# export MAVEN_OPTS="-Xmx2g -XX:ReservedCodeCacheSize=512m"
./dev/make-distribution.sh --name custom-spark --tgz --pip -Phadoop-2.7 -Phive -Pyarn -Pkubernetes

# Compile for a specific Hadoop version, for exmaple use this to compile for Hadoop 3
./dev/make-distribution.sh --name custom-spark --tgz --pip -Phadoop-3.2 -Pyarn -Pkubernetes
# old versions: ./dev/make-distribution.sh --name custom-spark --tgz --pip -Phadoop-2.7 -Dhadoop.version=3.2.0 -Pyarn -Pkubernetes

# compile a version with cherry-picked changes
# git checkout branch-2.3
# git cherry-pick xxxx

```

---
- Spark configuration
configuration files are: in SPARK_CONF_DIR (defaults SPARK_HOME/conf)  

```Scala  
// get configured parameters from running Spark Session with  
spark.conf.getAll.foreach(println)  
// get list of driver and executors from Spark Context:  
sc.getExecutorMemoryStatus.foreach(println)
```
 
```
# PySpark
from pyspark.conf import SparkConf
conf = SparkConf()
print(conf.toDebugString())
```

---
- Read and set configuration variables of Hadoop environment from Spark.
  Note this code works with the local JVM, i.e. the driver (will not read/write on executors's JVM)  
```
// Scala:
sc.hadoopConfiguration.get("dfs.blocksize")
sc.hadoopConfiguration.getValByRegex(".").toString.split(", ").sorted.foreach(println)
sc.hadoopConfiguration.setInt("parquet.block.size", 256*1024*1024)
```

```
# PySpark
sc._jsc.hadoopConfiguration().get("dfs.blocksize")
sc.hadoopConfiguration.set(key,value)
```

---
- Read filesystem statistics from all registered filesystem in Hadoop (notably HDFS and local, also s3a if used).  
  Note: this code reports statistics for the local JVM, i.e. the driver (will not read stats from executors)  
  Note: when using this programmatically, use `org.apache.hadoop.fs.FileSystem.getAllStatistics`, 
  `org.apache.hadoop.fs.FileSystem.getStatistics` also works. These options are being/have been deprecated.  
  See also extended statistics with the API getGlobalStorageStatistics example below.
```
scala> org.apache.hadoop.fs.FileSystem.printStatistics()
  FileSystem org.apache.hadoop.hdfs.DistributedFileSystem: 0 bytes read, 4130784 bytes written, 1 read ops, 0 large read ops, 3 write ops
  FileSystem org.apache.hadoop.fs.s3a.S3AFileSystem: 23562931 bytes read, 0 bytes written, 14591 read ops, 0 large read ops, 0 write ops
  FileSystem org.apache.hadoop.fs.RawLocalFileSystem: 0 bytes read, 0 bytes written, 0 read ops, 0 large read ops, 0 write ops
```

- Read extended filesystem statistics,  applies to Hadoop 2.8.0 and higher.

```scala
val stats=org.apache.hadoop.fs.FileSystem.getGlobalStorageStatistics.iterator
stats.forEachRemaining {entry =>
  println(s"Stats for scheme: ${entry.getScheme}")
  entry.getLongStatistics.forEachRemaining(println)
  println
  }
  ```
}
 
---
How to use the Spark Scala REPL to access Hadoop Filesystem API. Example for HDFS and s3a metrics:

```
// get Hadoop filesystem object
val fs = org.apache.hadoop.fs.FileSystem.get(sc.hadoopConfiguration)
// alternative:
val fs = org.apache.hadoop.fs.FileSystem.get(spark.sessionState.newHadoopConf)

//get local filesystem
val fslocal = org.apache.hadoop.fs.FileSystem.getLocal(spark.sessionState.newHadoopConf)

// get S3A Filesystem, 
// Use if you want to read metrics for s3a stats (or another Hadoop compatible filesystem)
val fullPathUri = java.net.URI.create("s3a://luca/")
val fs = org.apache.hadoop.fs.FileSystem.get(fullPathUri, spark.sessionState.newHadoopConf)
// alternative:
val fs = org.apache.hadoop.fs.FileSystem.get(fullPathUri,sc.hadoopConfiguration).asInstanceOf[org.apache.hadoop.fs.s3a.S3AFileSystem]

// Note, in the case of S3A/Hadoop v2.8.0 or higher this prints extended filesystem stats and S#A instrumentation values:
print(fs.toString)
// List of available statistics
fs.getStorageStatistics.forEach(println) 
// Get a single metric value:
fs.getInstrumentation.getCounterValue("stream_bytes_read")


// Silimarly for HDFS you can use this to explicitly cast to HDFS Client class:
val fullPathUri = java.net.URI.create("hdfs://myHDFSCLuster/")
val fs = org.apache.hadoop.fs.FileSystem.get(fullPathUri,sc.hadoopConfiguration).asInstanceOf[org.apache.hadoop.hdfs.DistributedFileSystem]


// get file status
fs.getFileStatus(new org.apache.hadoop.fs.Path("<file_path>"))

scala> fs.getFileStatus(new org.apache.hadoop.fs.Path("<file_path>")).toString.split("; ").foreach(println)
FileStatus{path=hdfs://analytix/user/canali/cms-dataset-20/20005/DE909CD0-F878-E211-AB7A-485B398971EA.root
isDirectory=false
length=2158964874
replication=3
blocksize=268435456
modification_time=1542653647906
access_time=1543245001357
owner=canali
group=supergroup
permission=rw-r--r--
isSymlink=false}


fs.getBlockSize(new org.apache.hadoop.fs.Path("<file_path>"))

fs.getLength(new org.apache.hadoop.fs.Path("<file_path>"))

// get block map
scala> fs.getFileBlockLocations(new org.apache.hadoop.fs.Path("<file_path>"), 0L, 2000000000000000L).foreach(println)
0,268435456,host1.cern.ch,host2.cern.ch,host3.cern.ch
268435456,268435456,host4.cern.ch,host5.cern.ch,host6.cern.ch
...
```
---
Example od analysis of Hadoop file data block locations using Spark SQL

```
bin/spark-shell
// get filesystem obejct
val fs = org.apache.hadoop.fs.FileSystem.get(sc.hadoopConfiguration)
// get blocks list (with replicas)
val l1=fs.getFileBlockLocations(new org.apache.hadoop.fs.Path("mydataset-20/20005/myfile1.parquet.snappy"), 0L, 2000000000000000L)
// transform in a Spark Dataframe
l1.flatMap(x => x.getHosts).toList.toDF("hostname").createOrReplaceTempView("filemap")
// query
spark.sql("select hostname, count(*) from filemap group by hostname").show

+-----------------+--------+
|         hostname|count(1)|
+-----------------+--------+
|mynode01.cern.ch|       5|
|mynode12.cern.ch|       4|
|mynode02.cern.ch|       4|
|mynode08.cern.ch|       3|
|mynode06.cern.ch|       6|
|...             |        |
+-----------------+--------+
```
---
- Print Properties
```
println(System.getProperties)
System.getProperties.toString.split(',').map(_.trim).foreach(println)

```
---
- Spark SQL execution plan, explain cost and code generation
```
sql("select count(*) from range(10) cross join range(10)").explain(true)
sql("explain select count(*) from range(10) cross join range(10)").collect.foreach(println)

// CBO
sql("explain cost select count(*) from range(10) cross join range(10)").collect.foreach(println)

// Print Code generation
sql("select count(*) from range(10) cross join range(10)").queryExecution.debug.codegen
sql("explain codegen select count(*) from range(10) cross join range(10)").collect.foreach(println)

for longer plans:
df.queryExecution.debug.codegenToSeq -> dumps to sequence of strings
df.queryExecution.debug.toFile -> dumps to filesystem file

```
---
- Spark SQL measure time spent in query plan parsing and optimization (Spark 3.0)

```
scala> val df=sql("select 1")

scala> df.queryExecution.tracker.
measureTime   phases   recordRuleInvocation   rules   topRulesByTime

scala> sql("select 1").queryExecution.tracker.
measurePhase   phases   recordRuleInvocation   rules   topRulesByTime

scala> sql("select 1").queryExecution.tracker.phases
scala> df.queryExecution.tracker.phases
resX: Map[String,org.apache.spark.sql.catalyst.QueryPlanningTracker.PhaseSummary] = Map(planning -> PhaseSummary(1547411782661, 1547411782824), optimization -> PhaseSummary(1547411782509, 1547411782648), parsing -> PhaseSummary(1547411764974, 1547411765852), analysis -> PhaseSummary(1547411765854, 1547411766069))
```
---
- Table and column statistics

Examples: as preparation create test tables and views
```
sql("create view v1 as select id, 't1' from range(10)") // vew in the default db namespace
sql("cache table my_cachedquery1 as select id, 'v2' from range(10)") //temporary table
sql("create table t1 as select id, 't1' from range(10)") // this requires hive support
```

Display catalog info:
```
spark.catalog.listDatabases.show(false)
spark.catalog.listTables.show(false)
```

Compute statistics on tables and cached views:
```
sql("analyze table t1 compute statistics")

// new in Spark 3.0, stats can be collected for cached views
sql("cache lazy table v1")
sql("analyze table v1 compute statistics")
```

Display table/view stats:
```
spark.table("v1").queryExecution.optimizedPlan.stats 
spark.table("v1").queryExecution.stringWithStats
sql("explain cost select * from v1").show(false)
```

Compute and display column stats on tables, cached queries and cached views:
```
sql("analyze table t1 compute statistics for all columns")

// Spark 3, allows to compute column stats on cached views in addition 
// to computing table defined in Hive metastore
sql("analyze table my_cachedquery1 compute statistics for all columns")
sql("analyze table v1 compute statistics for all columns")

spark.table("t1").queryExecution.optimizedPlan.stats.attributeStats
spark.table("my_cachedquery1").queryExecution.optimizedPlan.stats.attributeStats
spark.table("v1").queryExecution.optimizedPlan.stats.attributeStats

spark.table("t1").queryExecution.optimizedPlan.stats.attributeStats.foreach{case (k, v) => println(s"[$k]: $v")}

[id#0L]: ColumnStat(Some(10),Some(0),Some(9),Some(0),Some(8),Some(8),None,2)

```

Table statistics and column statistics histograms
```
sql("SET spark.sql.cbo.enabled=true")
sql("SET spark.sql.statistics.histogram.enabled=true")
spark.range(1000).selectExpr("id % 33 AS c0", "rand() AS c1", "0 AS c2").write.saveAsTable("t")
sql("ANALYZE TABLE t COMPUTE STATISTICS FOR COLUMNS c0, c1, c2")
spark.table("t").groupBy("c0").agg(count("c1").as("v1"), sum("c2").as("v2")).createTempView("temp")

spark.table("t").queryExecution.optimizedPlan.stats.attributeStats.foreach{case (k, v) => println(s"[$k]: $v")}
[c0#24320L]: ColumnStat(Some(33),Some(0),Some(32),Some(0),Some(8),Some(8),Some(Histogram(3.937007874015748,[Lorg.apache.spark.sql.catalyst.plans.logical.HistogramBin;@77c9db55)),2)
[c1#24321]: ColumnStat(Some(896),Some(7.45430597672625E-4),Some(0.9986498874940231),Some(0),Some(8),Some(8),Some(Histogram(3.937007874015748,[Lorg.apache.spark.sql.catalyst.plans.logical.HistogramBin;@258f3e5)),2)
[c2#24322]: ColumnStat(Some(1),Some(0),Some(0),Some(0),Some(4),Some(4),Some(Histogram(3.937007874015748,[Lorg.apache.spark.sql.catalyst.plans.logical.HistogramBin;@45f675a4)),2)

spark.table("temp").queryExecution.optimizedPlan.stats.attributeStats.foreach{case (k, v) => println(s"[$k]: $v")}
[c0#12161L]: ColumnStat(Some(33),Some(0),Some(32),Some(0),Some(8),Some(8),Some(Histogram(3.937007874015748,[Lorg.apache.spark.sql.catalyst.plans.logical.HistogramBin;@4d6cfa5)),2)
```


---
- Example command line for spark-shell/pyspark/spark-submit on YARN  
`spark-shell --master yarn --num-executors 5 --executor-cores 4 --executor-memory 7g --driver-memory 7g`

---
- Basic Scala methods to trigger actions for testing

This fetches the output and discards
 ```
sql("select id from range(10)").show
sql("select id from range(10)").collect
sql("select id from range(10)").foreach(_ => ()) // discards output
 ```
 
---
- Specify JAVA_HOME to use when running Spark on a YARN cluster   
```
export JAVA_HOME=/usr/lib/jvm/myJAvaHome # this is the JAVA_HOME of the driver
bin/spark-shell --conf spark.yarn.appMasterEnv.JAVA_HOME=/usr/lib/jvm/myJAvaHome --conf spark.executorEnv.JAVA_HOME=/usr/lib/jvm/myJAvaHome
```

---
- Run Pyspark on a Jupyter notebook
```
export PYSPARK_DRIVER_PYTHON=jupyter-notebook
# export PYSPARK_DRIVER_PYTHON=jupyter-lab
export PYSPARK_DRIVER_PYTHON_OPTS="--ip=`hostname` --no-browser --port=8888"
pyspark ...<add options here>
```
---
- Python UDF and pandas_udf, examples and tests

Examples of udf and pandas_udf. time.sleep is introduced for testing purposes
```python
def slowf(s):
  for i in range(10000):
    a = 2**i
  return a

import time
def slowf(s):
  for i in range(10000):
    a = 2**i
  time.sleep(10)
  return a

spark.udf.register("slowf", slowf)

sql("select slowf(1)").show()

sql("select avg(slowf(id)) from range(1000)").show()
```

```python
import pandas as pd
import time

from pyspark.sql.functions import col, pandas_udf
from pyspark.sql.types import LongType

def multiply_func(a, b):
  time.sleep(10)
  return a * b

multiply = pandas_udf(multiply_func, returnType=LongType())

spark.udf.register("multiply_func", multiply)

time.time()
sql("select multiply_func(1,1)").show()
time.time()

# By default pandas_udf batch 10000 rows (for each concurrently executing task)
# You expect that the execution time for 10k rows is the same as for 1 row for this exmaple
time.time()
sql("select avg(multiply_func(id,2)) from range(10000)").show()
time.time()
```

---
- Change Garbage Collector algorithm
  - For a discussion on tests with different GC algorithms for spark see the post [Tuning Java Garbage Collection for Apache Spark Applications](https://databricks.com/blog/2015/05/28/tuning-java-garbage-collection-for-spark-applications.html)
  - Example of how to use G1 GC: `--conf spark.driver.extraJavaOptions="-XX:+UseG1GC" --conf spark.executor.extraJavaOptions="-XX:+UseG1GC"` 

---
---
- Set log level in spark-shell and PySpark
If you have a SparkContext, use `sc.setLogLevel(newLevel)`

Otherwise edit or create the file log4j.properties in $SPARK_CONF_DIR (default SPARK_HOME/conf)
/bin/vi conf/log4j.properties
  
Example for the logging level of PySpark REPL  
```
log4j.logger.org.apache.spark.api.python.PythonGatewayServer=INFO
#log4j.logger.org.apache.spark.api.python.PythonGatewayServer=DEBUG
```

Example for the logging level of the Scala REPL:  
`log4j.logger.org.apache.spark.repl.Main=INFO`

---
- Caching dataframes using off-heap memory
```
bin/spark-shell --master local[*] --driver-memory 64g --conf spark.memory.offHeap.enabled=true --conf spark.memory.offHeap.size=64g --jars ../spark-measure_2.11-0.11-SNAPSHOT.jar
val df = sql("select * from range(1000) cross join range(10000)")
df.persist(org.apache.spark.storage.StorageLevel.OFF_HEAP)
```
---
- Other options for caching dataframes
```
df.persist(org.apache.spark.storage.StorageLevel.
DISK_ONLY     MEMORY_AND_DISK     MEMORY_AND_DISK_SER     MEMORY_ONLY     MEMORY_ONLY_SER     
DISK_ONLY_2   MEMORY_AND_DISK_2   MEMORY_AND_DISK_SER_2   MEMORY_ONLY_2   MEMORY_ONLY_SER_2   OFF_HEAP)
```

---
- Spark-root, read high energy physics data in ROOT format into Spark dataframes
```
bin/spark-shell --packages org.diana-hep:spark-root_2.11:0.1.16

val df = spark.read.format("org.dianahep.sparkroot").load("<path>/myrootfile.root")
val df = spark.read.format("org.dianahep.sparkroot.experimental").load("<path>/myrootfile.root")
```

---
- How to deploy Spark shell or a notebook behind a firewall
  - This is relevant when using spark-shell or pyspark or a Jupyter Notebook, 
  running the Spark driver on a client machine with a local firewall and
  accessing Spark executors remotely on a cluster
  - The driver listens on 2 TCP ports that need to be accessed by the executors on the cluster.
  This is how you can specify the port numbers (35000 and 35001 are picked just as an example):
```
--conf spark.driver.port=35000 
--conf spark.driver.blockManager.port=35001
```
  - You can set up the firewall rule on the driver to to allow connections from cluster node. 
  This is a simplified example of rule when using iptables:
```
-A INPUT -m state --state NEW -m tcp -p tcp -s 10.1.0.0/16 --dport 35000 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp -s 10.1.0.0/16 --dport 35001 -j ACCEPT
```
  - In addition clients may want to access the port for the WebUI (4040 by default)
 
---
- Get username and security details via Apache Hadoop security API
```
scala> org.apache.hadoop.security.UserGroupInformation.getCurrentUser()
res1: org.apache.hadoop.security.UserGroupInformation = luca@MYDOMAIN.COM (auth:KERBEROS)
```
---
- Distribute the Kerberos TGT cache to the executors
```bash
kinit    # get a Kerberos TGT if you don't already have one
klist -l # list details of Kerberos credentials file

spark-shell --master yarn --files <path to kerberos credentials file>#krbcache --conf spark.executorEnv.KRB5CCNAME='FILE:./krbcache'

pyspark --master yarn --files path to kerberos credentials file>#krbcache --conf spark.executorEnv.KRB5CCNAME='FILE:./krbcache'
```

---
- Run OS commands from Spark
```scala
// Scala, runs locally on the driver
import sys.process._
"uname -a".!  // with one !,  returns exit status
"uname -a".!! // with 2 !, returns output as String
```
- This execute OS commands on Spark executors (relevant for cluster deployments).
It is expected to run on each executor and for each "core"/task allocated.
However, the actual result and order are not guaranteed, a more solid approach is needed
```scala
// Scala, runs on the executors/tasks in a cluster
import sys.process._
sc.parallelize(1 to sc.defaultParallelism).map(_ => "uname -a" !).collect()
sc.parallelize(1 to sc.defaultParallelism).map(_ => "uname -a" !!).collect().foreach(println)
```
Alternative method to run OS commands on Spark executors in Scala
```
val a = sc.parallelize(1 to sc.defaultParallelism).map(x => org.apache.hadoop.util.Shell.execCommand("uname","-a")).collect()
val a = sc.parallelize(1 to sc.defaultParallelism).map(x => org.apache.hadoop.util.Shell.execCommand("/usr/bin/bash","-c","echo $PWD")).collect()
```
```
# Python, run on the executors (see comments in the Scala version) 
# method 1
import os
sc.parallelize(range(0, sc.defaultParallelism)).map(lambda i: os.system("uname -a")).collect()

# method 2
import subprocess
sc.parallelize(range(0, sc.defaultParallelism)).map(lambda i: subprocess.call(["uname", "-a"])).collect()
sc.parallelize(range(0, sc.defaultParallelism)).map(lambda i: subprocess.check_output(["uname", "-a"])).collect()
```

---
- Parquet tables
```
// Read
spark.read.parquet("fileNameAndPath")
// relevant configuration:
spark.conf.set("spark.sql.files.maxPartitionBytes", ..) // default 128MB, small files are grouped into partitions up to this size

// Write
df.write
  .coalesce(N_partitions)   // use this if you want to reduce the number of output partitions (beware that it also affects num of concurrent write tasks) 
  .partitionBy("colPartition1", "colOptionalSubPart") // partitioning column(s) 
  .bucketBy(numBuckets, "colBucket")   // This feature currently gives error with save, follow SPARK-19256 or use saveAsTable (Hive)
  .format("parquet")
  .save("filePathandName")             // you can use saveAsTable as an alternative

//Options
.option("parquet.block.size", <blockSize>) // defalut 128MB, see also c.hadoopConfiguration.setInt("parquet.block.size", <blocksize>
.option("compression", <compression_codec>) // default snappy, see also spark.sql.parquet.compression.codec

// relevant configuration parameters:
sc.hadoopConfiguration.setInt("parquet.block.size", .. ) // default to 128 MB parquet block size (size of the column groups)
spark.conf.set("spark.sql.parquet.compression.codec","xxx") // xxx= none, gzip, lzo, snappy, {zstd, brotli, lz4} 
spark.conf.set("spark.sql.files.maxRecordsPerFile", ...) // defaults to 0, use if you need to limit size of files being written  
```

// Savemode:
df.coalesce(4).write.mode(org.apache.spark.sql.SaveMode.Overwrite).parquet("..PATH..")

---
- Repartition / Compact Parquet tables

Parquet table repartition is an operation that you may want to use in the case you ended up with
multiple small files into each partition folder and want to compact them in a smaller number of larger files.
Example:  
```
val df = spark.read.parquet("myPartitionedTableToComapct")
df.repartition('colPartition1,'colOptionalSubPartition)
  .write.partitionBy("colPartition1","colOptionalSubPartition")
  .format("parquet")
  .save("filePathandName")
```
---
- Read from Oracle via JDBC, example from [Spark_Oracle_JDBC_Howto.md](Spark_Oracle_JDBC_Howto.md)
```
val df = spark.read.format("jdbc")
         .option("url", "jdbc:oracle:thin:@dbserver:port/service_name")
         .option("driver", "oracle.jdbc.driver.OracleDriver")
         .option("dbtable", "MYSCHEMA.MYTABLE")
         .option("user", "MYORAUSER")
         .option("password", "XXX")
         .option("fetchsize",10000).load()
         
// test
df.printSchema
df.show(5)
         
// write data as compressed Parquet files  
df.write.parquet("MYHDFS_TARGET_DIR/MYTABLENAME")
```

---
- Enable short-circuit reads for Spark on a Hadoop cluster
  - Spark executors need to have libhadoop.so in the library path
  - Short-circuit is a good feature to enable for Spark running on a Hadoop clusters as it improves performance of I/O
  that is local to the Spark executors.
  - Note: the warning message "WARN shortcircuit.DomainSocketFactory: The short-circuit local reads feature cannot be used because libhadoop cannot be loaded"
  is generated after checking on the driver machine. This can be misleading if the driver is not part of the Hadoop cluster, as what is important is that short-circuit is enabled on the executors!  
  - if the library path of the executors as set up on the system defaults does not yet allow to find libhadoop.so, this can be used:
`--conf spark.executor.extraLibraryPath=/usr/lib/hadoop/lib/native --conf spark.driver.extraLibraryPath=/usr/lib/hadoop/lib/native`

---
- Spark-shell power mode and change config to avoid truncating print for long strings
  - Enter power mode set max print string to 1000:
  - BTW, see more spark shell commands: `:help`

```
spark-shell
scala> :power
Power mode enabled. :phase is at typer.
import scala.tools.nsc._, intp.global._, definitions._
Try :help or completions for vals._ and power._

vals.isettings.maxPrintString=1000
```

---
 - Examples of Dataframe creation for testing
 ```
sql("select * from values (1, 'aa'), (2,'bb'), (3,'cc') as (id,desc)").show
+---+----+
| id|desc|
+---+----+
|  1|  aa|
|  2|  bb|
|  3|  cc|
+---+----+

sql("select * from values (1, 'aa'), (2,'bb'), (3,'cc') as (id,desc)").createOrReplaceTempView("t1")
spark.table("t1").printSchema
root
 |-- id: integer (nullable = false)
 |-- desc: string (nullable = false)

spark.sql("create or replace temporary view outer_v1 as select * from values (1, 'aa'), (2,'bb'), (3,'cc') as (id,desc)")

sql("select id, floor(200*rand()) bucket, floor(1000*rand()) val1, floor(10*rand()) val2 from range(10)").show(3)
+---+------+----+----+
| id|bucket|val1|val2|
+---+------+----+----+
|  0|     1| 223|   5|
|  1|    26| 482|   5|
|  2|    42| 384|   7|
+---+------+----+----+
only showing top 3 rows

scala> val df=Seq((1, "aaa", Map(1->"a") ,Array(1,2,3), Vector(1.1,2.1,3.1)), (2, "bbb", Map(2->"b") ,Array(4,5,6), Vector(4.1,5.1,6.1))).toDF("id","name","map","array","vector")
df: org.apache.spark.sql.DataFrame = [id: int, name: string ... 3 more fields]

df.printSchema
root
 |-- id: integer (nullable = false)
 |-- name: string (nullable = true)
 |-- map: map (nullable = true)
 |    |-- key: integer
 |    |-- value: string (valueContainsNull = true)
 |-- array: array (nullable = true)
 |    |-- element: integer (containsNull = false)
 |-- vector: array (nullable = true)
 |    |-- element: double (containsNull = false)


df.show
+---+----+-----------+---------+---------------+
| id|name|        map|    array|         vector|
+---+----+-----------+---------+---------------+
|  1| aaa|Map(1 -> a)|[1, 2, 3]|[1.1, 2.1, 3.1]|
|  2| bbb|Map(2 -> b)|[4, 5, 6]|[4.1, 5.1, 6.1]|
+---+----+-----------+---------+---------------+

scala> case class myclass(id: Integer, name: String, myArray: Array[Double])
scala> val df=Seq(myclass(1, "aaaa", Array(1.1,2.1,3.1)),myclass(2, "bbbb", Array(4.1,5.1,6.1))).toDF
scala> df..show
+---+----+---------------+
| id|name|        myArray|
+---+----+---------------+
|  1|aaaa|[1.1, 2.1, 3.1]|
|  2|bbbb|[4.1, 5.1, 6.1]|
+---+----+---------------+

// Dataset API
scala> df.as[myclass]
res75: org.apache.spark.sql.Dataset[myclass] = [id: int, name: string ... 1 more field]

scala> df.as[myclass].map(v  => v.id + 1).reduce(_ + _)
res76: Int = 5

// Manipulating rows, columns and arrays

// collect_list agregates columns into rows
sql("select collect_list(col1) from values 1,2,3").show
+------------------+
|collect_list(col1)|
+------------------+
|         [1, 2, 3]|
+------------------+

// explode transforms aggregates into columns
sql("select explode(Array(1,2,3))").show
+---+
|col|
+---+
|  1|
|  2|
|  3|
+---+

sql("select col1, explode(Array(1,2,3)) from values Array(1,2,3)").show()
+---------+---+
|     col1|col|
+---------+---+
|[1, 2, 3]|  1|
|[1, 2, 3]|  2|
|[1, 2, 3]|  3|
+---------+---+

// collect_list and explode combined, return to orginial values 
sql("select collect_list(col1) from values 1,2,3").show
sql("select collect_list(col) from (select explode(Array(1,2,3)))").show
+-----------------+
|collect_list(col)|
+-----------------+
|        [1, 2, 3]|
+-----------------+

// How to push a filter on a nested field in a DataFrame
// The general strategy is to unpack the array, apply a filter then repack
// Note, Higher order functions in Spark SQL and other topics relatedon how to improve this
// are discussed at https://databricks.com/blog/2017/05/24/working-with-nested-data-using-higher-order-functions-in-sql-on-databricks.html
// Example:
sql("select col1, collect_list(col) from (select col1, explode(col1) as col from values Array(1,2,3),Array(4,5,6)) where col%2 = 0 group by col1").show()

+---------+-----------------+
|     col1|collect_list(col)|
+---------+-----------------+
|[1, 2, 3]|              [2]|
|[4, 5, 6]|           [4, 6]|
+---------+-----------------+

// Example of usage of laterral view
sql("select * from values 'a','b' lateral view explode(Array(1,2)) tab1").show()
+----+---+
|col1|col|
+----+---+
|   a|  1|
|   a|  2|
|   b|  1|
|   b|  2|
+----+---+

```

---
 - Additional examples of dealing with nested structures in Spark SQL
```
scala> dsMuons.printSchema
root
 |-- muons: array (nullable = true)
 |    |-- element: struct (containsNull = true)
 |    |    |-- reco::Candidate: struct (nullable = true)
 |    |    |-- qx3_: integer (nullable = true)
 |    |    |-- pt_: float (nullable = true)
 |    |    |-- eta_: float (nullable = true)
 |    |    |-- phi_: float (nullable = true)
 |    |    |-- mass_: float (nullable = true)
 |    |    |-- vertex_: struct (nullable = true)
 |    |    |    |-- fCoordinates: struct (nullable = true)
 |    |    |    |    |-- fX: float (nullable = true)
 |    |    |    |    |-- fY: float (nullable = true)
 |    |    |    |    |-- fZ: float (nullable = true)
 |    |    |-- pdgId_: integer (nullable = true)
 |    |    |-- status_: integer (nullable = true)
 |    |    |-- cachePolarFixed_: struct (nullable = true)
 |    |    |-- cacheCartesianFixed_: struct (nullable = true)


// the following 2 are equivalent and transform an array of struct into a table-like  format
// explode can be used to deal withArrays
// to deal with structs use "col.*"

dsMuons.createOrReplaceTempView("t1")
sql("select element.* from (select explode(muons) as element from t1)").show(2)

dsMuons.selectExpr("explode(muons) as element").selectExpr("element.*").show(2)

+---------------+----+---------+----------+----------+----------+--------------------+------+-------+----------------+--------------------+
|reco::Candidate|qx3_|      pt_|      eta_|      phi_|     mass_|             vertex_|pdgId_|status_|cachePolarFixed_|cacheCartesianFixed_|
+---------------+----+---------+----------+----------+----------+--------------------+------+-------+----------------+--------------------+
|             []|  -3|1.7349417|-1.6098186| 0.6262487|0.10565837|[[0.08413784,0.03...|    13|      0|              []|                  []|
|             []|  -3| 5.215807|-1.7931011|0.99229723|0.10565837|[[0.090448655,0.0...|    13|      0|              []|                  []|
+---------------+----+---------+----------+----------+----------+--------------------+------+-------+----------------+--------------------+

```
---
- Multi select statements in Spark sql
Example:
```
scala> sql("from range(10) select id where id>5 select id+10 where id<4").show
+---+
| id|
+---+
|  6|
|  7|
|  8|
|  9|
| 10|
| 11|
| 12|
| 13|
+---+
```
---
- Spark SQL aggregate funcitions, SQl vs. declarative API

  - spark-shell:
  ```
  val df=sql("select id, id % 3 id2 from range(10)")
  df.groupBy('id2).agg(avg('id)).show
  ```
  - sql:
  ```
  sql("select id, id % 3 id2 from range(10)").createOrReplaceTempView("t1")
  sql("select id2, avg(id) from t1 group by id2").show
  ```

---
Spark binaryfile format (Spark 3.0)
Example:
```
scala> val df = spark.read.format("binaryFile").load("README.md")
df: org.apache.spark.sql.DataFrame = [path: string, modificationTime: timestamp ... 2 more fields]

scala> df.count
res2: Long = 1

scala> df.show
+--------------------+-------------------+------+--------------------+
|                path|   modificationTime|length|             content|
+--------------------+-------------------+------+--------------------+
|file:///home/luca...|2019-04-24 21:20:23|  4620|[23 20 41 70 61 6...|
+--------------------+-------------------+------+--------------------+
```
---
- Spark TPCDS benchmark
  - Download and build the Spark package from [https://github.com/databricks/spark-sql-perf]
  - Download and build tpcds-kit for generating data from [https://github.com/databricks/tpcds-kit]
  - Testing
    1. Generate schema
    2. Run benchmark
    3. Extract results

See instructions at the [spark-sql-perf](https://github.com/databricks/spark-sql-perf) git repo
for additional info on how to generate data and tun the package. Here some pointers/examples:
```
///// 1. Generate schema
bin/spark-shell --master yarn --num-executors 25 --driver-memory 12g --executor-memory 12g --executor-cores 4 --jars /home/luca/spark-sql-perf-new/target/scala-2.11/spark-sql-perf_2.11-0.5.1-SNAPSHOT.jar

NOTES:
  - Each executor will spawn dsdgen to create data, using the parameters for size (e.g. 10000) and number of partitions (e.g. 1000)
  - Example: bash -c cd /home/luca/tpcds-kit/tools && ./dsdgen -table catalog_sales -filter Y -scale 10000 -RNGSEED 100 -parallel 1000 -child 107
  - Each "core" in the executor spawns one dsdgen
  - This workloads is memory hungry, to avoid excessive GC activity, allocate abundant memory per executor core

val tables = new com.databricks.spark.sql.perf.tpcds.TPCDSTables(spark.sqlContext, "/home/luca/tpcds-kit/tools", "10000")
tables.genData("/user/luca/TPCDS/tpcds_10000", "parquet", true, true, true, false, "", 100)

///// 2. Run Benchmark 
export SPARK_CONF_DIR=/usr/hdp/spark/conf
export HADOOP_CONF_DIR=/etc/hadoop/conf
export LD_LIBRARY_PATH=/usr/hdp/hadoop/lib/native/
cd spark-2.4.3-bin-hadoop2.7

bin/spark-shell --master yarn --num-executors 40 --executor-cores 4  --driver-memory 12g  --executor-memory 12g --jars /home/luca/spark-sql-perf-new/target/scala-2.11/spark-sql-perf_2.11-0.5.1-SNAPSHOT.jar --conf spark.sql.crossJoin.enabled=true
// if using larger number of cores consider bumping up --conf spark.sql.shuffle.partitions=400
// if running on k8s client mode, add: --conf spark.task.maxDirectResultSize=100000000000 to work around SPARK-26087

sql("SET spark.sql.perf.results=/user/luca/TPCDS/perftest_results")
import com.databricks.spark.sql.perf.tpcds.TPCDSTables
val tables = new TPCDSTables(spark.sqlContext, "/home/luca/tpcds-kit/tools","10000")

///// 3. Setup tables and run benchmask

tables.createTemporaryTables("/user/luca/TPCDS/tpcds_10000", "parquet")
val tpcds = new com.databricks.spark.sql.perf.tpcds.TPCDS(spark.sqlContext)

// Run benchmark
val experiment = tpcds.runExperiment(tpcds.tpcds2_4Queries)

// optionally: experiment.waitForFinish(timeout)

// Example of how to put exclude list (or similarly use for include lists) to limit number of querries:
//val benchmarkQueries = for (q <- tpcds.tpcds1_4Queries if !q.name.matches("q14a-v1.4|q14b-v1.4|q72-v1.4")) yield(q)
//val experiment = tpcds.runExperiment(benchmarkQueries)

///// 4. Extract results
experiment.currentResults.toDF.createOrReplaceTempView("currentResults")

spark.sql("select name, min(executiontime) as MIN_Exec, max(executiontime) as MAX_Exec, avg(executiontime) as AVG_Exec_Time_ms from currentResults group by name order by name").show(200)
spark.sql("select name, min(executiontime) as MIN_Exec, max(executiontime) as MAX_Exec, avg(executiontime) as AVG_Exec_Time_ms from currentResults group by name order by name").repartition(1).write.csv("TPCDS/test_results_<optionally_add_date_suffix>.csv")

///// Use CBO, modify step 3 as follows

// one-off: setup tables using catalog (do not use temporary tables as in example above
tables.createExternalTables("/user/luca/TPCDS/tpcds_1500", "parquet", "tpcds1500", overwrite = true, discoverPartitions = true)
// compute statistics
tables.analyzeTables("tpcds1500", analyzeColumns = true) 

tables.createExternalTables("/user/luca/TPCDS/tpcds_1500", "parquet", "tpcds10000", overwrite = true, discoverPartitions = true)
tables.analyzeTables("tpcds10000", analyzeColumns = true) 

spark.conf.set("spark.sql.cbo.enabled",true)
// --conf spark.sql.cbo.enabled=true
sql("use tpcds10000")
sql("show tables").show

spark.conf.set("spark.sql.cbo.enabled",true)
// --conf spark.sql.cbo.enabled=true
```

---
- Generate simple benchmark load, CPU-bound with Spark
  - Note: scale up the tests by using larger test tables, that is extending the (xx) value in "range(xx)"
```  
bin/spark-shell --master local[*]

// 1. Test Query 1
spark.time(sql("select count(*) from range(10000) cross join range(1000) cross join range(100)").show)
  
// 2. Test Query 2
// this other example exercices more code path in Spark execution
sql("select id, floor(200*rand()) bucket, floor(1000*rand()) val1, floor(10*rand()) val2 from range(1000000)").cache().createOrReplaceTempView("t1")
sql("select count(*) from t1").show()
 
spark.time(sql("select a.bucket, sum(a.val2) tot from t1 a, t1 b where a.bucket=b.bucket and a.val1+b.val1<1000 group by a.bucket order by a.bucket").show())
```

---
- Monitor Spark workloads with Dropwizard metrics for Spark, Influxdb Grafana   
  - Three main steps: (A) configure [Dropwizard (codahale) Metrics library](https://metrics.dropwizard.io) for Spark
   (B) sink the metrics to influxdb
   (C) Setup Grafana dashboards to read the metrics from InfluxDB 
  - See [Spark Performance Dashboard](../Spark_Dashboard)
---
- Spark has 2 configurable metrics sources in the driver introduced by [SPARK-26285](https://issues.apache.org/jira/browse/SPARK-26285)
  - The namespace is AccumulatorSource
  - The metrics are: DoubleAccumulatorSource, LongAccumulatorSource
  - They allow to export accumulator variables (LongAccumulator and DoubleAccumulator)
  . These metrics can be used in the grafana dashboard or with other sinks
  - Example:
```
import org.apache.spark.util.{AccumulatorV2, DoubleAccumulator, LongAccumulator}
import org.apache.spark.metrics.source.{DoubleAccumulatorSource, LongAccumulatorSource}
val acc1 = new LongAccumulator()
LongAccumulatorSource.register(spark.sparkContext, Map("my-accumulator-1" -> acc1))
scala> acc1.value
res5: Long = 0

scala> acc1.add(1L)
scala> acc1.value

This will appear in the sink, for example as a record:
my-accumulator-1,applicationid=application_1549330477085_0257,namespace=AccumulatorSource,process=driver,username=luca
```

---
- How to access AWS s3 Filesystem with Spark  
  -  Deploy the jars for hadoop-aws with the implementation of S3A as an Hadoop filesystem.  
  -  The following lists multiple (redundant) ways to set the Hadoop client configuration 
  for s3a in the Spark driver JVM.Spark executors will take care of setting the Hadoop client
  configuration in the classpath of executors's JVM (see org.apache.spark.deploy.SparkHadoopUtil.scala).
  ```
  export AWS_SECRET_ACCESS_KEY="XXXX..." # either set this or use spark conf as listed below: multiple ways to config 
  export AWS_ACCESS_KEY_ID="YYYY..."
  bin/spark-shell \
    --conf spark.hadoop.fs.s3a.endpoint="https://s3.cern.ch" \
    --conf spark.hadoop.fs.s3a.impl="org.apache.hadoop.fs.s3a.S3AFileSystem" \
    --conf spark.hadoop.fs.s3a.secret.key="XXX..." \
    --conf spark.hadoop.fs.s3a.access.key="YYY..." \
    --packages org.apache.hadoop:hadoop-aws:2.7.7 # edit hadoop-aws version to match Spark's Hadoop

  # example of how to use
  val df=spark.read.parquet("s3a://datasets/tpcds-1g/web_sales")
  df.count
  ```
  - Note, I have tested this on Spark compiled for Hadoop 3.2 and with Hadoop 2.7.  
  I have noticed that Hadoop 3.2/hadoop-aws 3.2 reading from s3.cern.ch gets stuck when listing 
  directories with a large number of files (as in the TPCDS benchmark). The workaround is:
  ```
  --packages org.apache.hadoop:hadoop-aws:3.2.0
  --conf spark.hadoop.fs.s3a.list.version=1
  ```
  - hadoop-aws package will also cause the pull of dependencies from com.amazonaws:aws-java-sdk:version
  - note: use `s3cmd la` to list available s3 buckets


  - More configuration options (alternatives to the recipe above): 
    - Set config in driver's Hadoop client
     ```
     sc.hadoopConfiguration.set("fs.s3a.endpoint", "https://s3.cern.ch") 
     sc.hadoopConfiguration.set("fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
     sc.hadoopConfiguration.set("fs.s3a.secret.key", "XXXXXXXX..")
     sc.hadoopConfiguration.set("fs.s3a.access.key", "YYYYYYY...")
     
     // note for Python/PySpark use sc._jsc.hadoopConfiguration().set(...)
     ```
    - Set config in Hadoop client core-site.xml 
     ```
     <property>
       <name>fs.s3a.secret.key</name>
       <value>XXXX</value>
     </property>
   
     <property>
       <name>fs.s3a.access.key</name>
       <value>YYYY</value>
     </property>
   
     <property>
       <name>fs.s3a.endpoint</name>
       <value>https://s3.cern.ch</value>
     </property>
   
     <property>
       <name>fs.s3a.impl</name>
       <value>org.apache.hadoop.fs.s3a.S3AFileSystem</value>
     </property>
    ```
---
- How to use/choose pyspark version to import from python
  - simple way to make import pyspark work in python (`pip install pyspark`)
  - more sofisticated: you want to choose the Spark version and/or (re)use an existing Spark home:
     ```
        pip install findspark
        
        python
        import findspark
        findspark.init('/home/luca/Spark/spark-2.4.0-bin-hadoop2.7') #set path to SPARK_HOME
     ```
  - note: when using bin/pyspark, this is not relevant, 
    as pyspark from the current SPARK_HOME will be used in this case
 ---
 - How to add a description to a Spark job:
   - spark.sparkContext.setJobDescription("job description")
   - Note: in Spark 3.0, when using Spark SQL/Dataframes: "job description" will be displayed in SQL tab
   - See also: spark.sparkContext.setJobGroup(groupId: String,description: String,interruptOnCancel: Boolean)
 
 ---
 Salting SQL joins to work around problems with data skew on large tables, exmaple:
Add a salt column to the tables to be joined:
```
val df1b = df1.selectExpr("id1", "key1", "name1", "int(rand()*10) as salt1")
val df2b = df2.selectExpr("id2", "key2", "name2", "int(rand()*10) as salt2")
 ```
Transform the query
```
// original join
df1.join(df2, 'key1==='key2)

// join using the salt column
df1b.join(df2b, 'key1==='key2 and 'salt1==='salt2)
``` 
---
Spark SQL hints for join are:  
"broadcast" -> Spark 2.x,
"merge", "shuffle_hash", "shuffle_replicate_nl" -> Spark 3.0

Examples, note for sql use /*+ hint_name(t1, t2)*/:
```
val df1 = spark.sql("select id as id1, id % 2 as key1, 'aaaaaaaa' name1 from range(100)")
val df2 = spark.sql("select id+5 id2, id % 2 as key2, 'bbbbbbbbb' name2 from range(100)")
df1.join(df2, 'key1==='key2).explain(true)

df1.hint("broadcast").join(df2, 'key1==='key2).explain(true)
df1.hint("merge").join(df2, 'key1==='key2).explain(true)
df1.hint("shuffle_hash").join(df2, 'key1==='key2).explain(true)
df1.hint("shiffle_replicate_nl").join(df2, 'key1==='key2).explain(true)
``` 
---
Use of regular expression in Spark SQL, example and gotcha:
When using SQL or selectExpr, you need to double the backslashes (maybe a bug?)
```
val df=sql("select id, 'aadd ffggg sss wwwaaa' name from range(10)")
df.selectExpr("regexp_extract(name, '(\\\\w+)', 0)").show(2)
```
All OK with the direct use of the function:
```
df.select(regexp_extract(col("name"), "(\\w+)", 0)).show(2)
```

