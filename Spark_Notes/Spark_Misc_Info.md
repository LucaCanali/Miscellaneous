## Spark Miscellaneous - Info, commands, and tips

- Explicitly allocate a Spark Session
```
// Scala
import org.apache.spark.sql._
val spark = SparkSession.
    builder().
    appName("my app").
    master("local[*]").   // use master("yarn") for a YARN cluster
    config("spark.driver.memory","2g").  // set config the parameters as needed
    getOrCreate() 

# Python
from pyspark.sql import SparkSession
spark = SparkSession.builder \
        .appName("my app")  \
        .master("local[*]") \
        .config("spark.driver.memory","2g") \
        .getOrCreate()

# Note: optionally choose which Python to use
# Run this before starting PySpark 
export PYSPARK_PYTHON=...
```
---
- How to use/choose Spark/PySpark home to use from python
  - simple way to make import pyspark work in python (`pip install pyspark`)
  - more sophisticated: you want to choose the Spark version and/or (re)use an existing Spark home:
     ```
        # pip install findspark

        import findspark
        findspark.init('/home/luca/Spark/spark-3.3.1-bin-hadoop3') #set path to SPARK_HOME
     ```
  - note: when using bin/pyspark, this is not relevant,
    as pyspark from the current SPARK_HOME will be used in this case
---
- Workload profile with [sparkMeasure](Spark_Performace_Tool_sparkMeasure.md)
```
bin/spark-shell --packages ch.cern.sparkmeasure:spark-measure_2.12:0.22
val stageMetrics = ch.cern.sparkmeasure.StageMetrics(spark) 
stageMetrics.runAndMeasure(spark.sql("select count(*) from range(1000) cross join range(1000)").show)
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
- How to read SQL Metrics using Status Store
```
val df=spark.sql("select count(*) from range(10) join range(10)")
df.collect()

val statusStore = spark.sharedState.statusStore
val lastExecId = statusStore.executionsList.last.executionId
val executionMetrics = statusStore.execution(lastExecId).get.metrics.mkString

statusStore.planGraph(0).nodes(2).metrics
statusStore.executionMetrics(0)
```

from Python:
```python
df=spark.sql("select count(*) from range(10) join range(10)")
df.collect()

statusStore=spark._jsparkSession.sharedState().statusStore()
spark._jsparkSession.sharedState().statusStore().executionMetrics(0).toString()

statusStore = self.spark._jsparkSession.sharedState().statusStore()
lastExecId = statusStore.executionsList().last().executionId()
executionMetrics = statusStore.execution(lastExecId).get().metrics().mkString()
```

---
- How to build Spark
  - see also https://spark.apache.org/docs/latest/building-spark.html
```
git clone https://github.com/apache/spark.git
cd spark
# export MAVEN_OPTS="-Xmx2g -XX:ReservedCodeCacheSize=512m"

# Compile for a specific Hadoop version, for example use this to compile for Hadoop 3.2
./dev/make-distribution.sh --name custom-spark --tgz --pip -Phadoop-3.2 -Pyarn -Pkubernetes

```
--- 
- Spark executor plugins  
Executor plugins allow to run custom code at Executor startup. The y can be useful to extend instrumentation/monitoring and for 
advanced configuration. See examples at:
  - [Spark executo plugin for Spark 2.4](https://github.com/cerndb/SparkExecutorPlugins2.4)
  - [Spark executor plugin for Spark 3.0](https://github.com/cerndb/SparkExecutorPlugins)
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
  Note this code works with the local JVM, i.e. the driver (will not read/write on executors' JVM)  
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

// Note, in the case of S3A/Hadoop v2.8.0 or higher this prints extended filesystem stats and S3A instrumentation values:
print(fs.toString)
// List of available statistics
fs.getStorageStatistics.forEach(println) 
fs.getStorageStatistics.getLongStatistics.forEachRemaining(println)
// Get a single metric value:
fs.getInstrumentation.getCounterValue("stream_bytes_read")
fs.getStorageStatistics.getLong("stream_bytes_read")

// Similarly for HDFS you can use this to explicitly cast to HDFS Client class:
val fullPathUri = java.net.URI.create("hdfs://myHDFSCLuster/")
val fs = org.apache.hadoop.fs.FileSystem.get(fullPathUri,sc.hadoopConfiguration).asInstanceOf[org.apache.hadoop.hdfs.DistributedFileSystem]

// get file status
fs.getFileStatus(new org.apache.hadoop.fs.Path("<file_path>"))

scala> fs.getFileStatus(new org.apache.hadoop.fs.Path("<file_path>")).toString.split("; ").foreach(println)
FileStatus{path=hdfs://cluster/user/myusername/cms-dataset-20/20005/DE909CD0-F878-E211-AB7A-485B398971EA.root
isDirectory=false
length=2158964874
replication=3
blocksize=268435456
modification_time=1542653647906
access_time=1543245001357
owner=myusername
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
List directory and read files,  
Example with root files and laurelin

```
spark-shell --master yarn --num-executors 4 --executor-memory 32g --executor-cores 8 --driver-memory 8g --packages edu.vanderbilt.accre:laurelin:1.1.1


// val fs = org.apache.hadoop.fs.FileSystem.get(sc.hadoopConfiguration)

val fullPathUri = java.net.URI.create("root://eospublic.cern.ch/")
val fs = org.apache.hadoop.fs.FileSystem.get(fullPathUri,sc.hadoopConfiguration).asInstanceOf[ch.cern.eos.XRootDFileSystem]

val dirListing = fs.listFiles(new org.apache.hadoop.fs.Path("root://eospublic.cern.ch/eos/root-eos/benchmark/CMSOpenDataDimuon"), false)

import scala.collection.mutable.ListBuffer
val rootFiles = new ListBuffer[String]()

while (dirListing.hasNext) {
  val filePath = dirListing.next.getPath.toString
  if (filePath matches("^.+.root$")) {
    rootFiles += filePath
  }
}


val df=spark.read.format("root").option("tree", "Events").load(rootFiles:_*)

df.printSchema()
```
---
PySpark list files in a directory
```
fs = sc._jvm.org.apache.hadoop.fs.FileSystem.get(sc._jsc.hadoopConfiguration())
status = fs.listStatus(sc._jvm.org.apache.hadoop.fs.Path("/mypath_here/"))
for fileStatus in status:
    print(fileStatus.getPath())
```
---
Example analysis of Hadoop file data block locations using Spark SQL

```
bin/spark-shell
// get filesystem object
val fs = org.apache.hadoop.fs.FileSystem.get(sc.hadoopConfiguration)
// get blocks list (with replicas)
val l1=fs.getFileBlockLocations(new org.apache.hadoop.fs.Path("mydataset-20/20005/myfile1.parquet.snappy"), 0L, 2000000000000000L)
// transform into a Spark Dataframe
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

// New in Spark 3.0, explain foramtted
sql("explain formatted select count(*) from range(10) cross join range(10)").collect.foreach(println)
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

Examples of udf and pandas_udf (of type SCALAR) using Spark SQL.
Note: time.sleep is introduced for testing purposes
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


Example with pandas_udf
```python
from pyspark.sql.functions import pandas_udf

@pandas_udf("long")
def test_pandas(col1):
  return col1 * col1

res = spark.range(10).select(test_pandas("id")).collect()

# register to use with SQL
spark.udf.register("test_pandas", test_pandas)
res = spark.sql("select test_pandas(id) from range(10)").collect()

import time
start = time.time()
res = spark.sql("select test_pandas(id) from range(10000)").collect()
end = time.time()
print(end - start)

# syntax with type hint
@pandas_udf("float")
def product(a: pd.Series, b) -> pd.Series:
  val = a * b
  return val

spark.udf.register("product", product)

# Python pandas_udf returning a struct using pd.DataFrame

from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf("struct<p0x float, p1x float>")
def z_candidates(p0x: pd.Series, p1x: pd.Series) -> pd.DataFrame:
  ret_val = pd.concat([p0x, p1x], axis=1, join="inner").rename(columns={"_0": "p0x", "_1": "p1x"})
  return ret_val

spark.udf.register("z_candidates", z_candidates)

df_4lep_test = df_4lep.selectExpr("z_candidates(P0x, P1X)")
df_4lep_test.printSchema()

root
|-- z_candidates(P0x, P1X): struct (nullable = true)
|    |-- p0x: float (nullable = true)
|    |-- p1x: float (nullable = true)
```
---
- How to use a Scala UDF in Python:
- On the Python side:
  ```
  # Scala UDF
  # Computes the dimuon invarian mass
  
  from pyspark.sql.types import FloatType
  spark.udf.registerJavaFunction("product", "ch.cern.udf.product", FloatType())
  
  df.selectExpr("product(a,b)")
  ```
- Scala UDF
  ```
  package ch.cern.udf
  import org.apache.spark.sql.api.java._
  class DimuonMass extends UDF2[Float, Float, Float] {
    def call(a: Float, b: Float): Float = {
      val ret = a * b
      E
    }
  }  
  ```
- Build the Scala UDF and add the jar as a Spark config `.config("spark.jars", "path_tojar")`

---
- Change Garbage Collector algorithm
  - For a discussion on tests with different GC algorithms for spark see the post [Tuning Java Garbage Collection for Apache Spark Applications](https://databricks.com/blog/2015/05/28/tuning-java-garbage-collection-for-spark-applications.html)
  - Example of how to use G1 GC: `--conf spark.driver.extraJavaOptions="-XX:+UseG1GC" --conf spark.executor.extraJavaOptions="-XX:+UseG1GC"` 

---
- Set log level in spark-shell and PySpark
If you have a SparkContext, use `sc.setLogLevel(newLevel)`

Otherwise, edit or create the file log4j.properties in $SPARK_CONF_DIR (default SPARK_HOME/conf)
/bin/vi conf/log4j.properties
  
Example for the logging level of PySpark REPL  
```
log4j.logger.org.apache.spark.api.python.PythonGatewayServer=INFO
#log4j.logger.org.apache.spark.api.python.PythonGatewayServer=DEBUG
```

Example for the logging level of the Scala REPL:  
`log4j.logger.org.apache.spark.repl.Main=INFO`

---
- Caching dataframes 
- caching is lazy, so you need to trigger an action, as in `df.cache.count`
- By default caching of Spark dataframes uses persist with level MEMORY_AND_DISK.
- Note this is different for rdd, caching on rdd uses by default MEMORY_ONLY
- Scala:
  ```
  df.persist(org.apache.spark.storage.StorageLevel.
  DISK_ONLY     MEMORY_AND_DISK     MEMORY_AND_DISK_SER     MEMORY_ONLY     MEMORY_ONLY_SER     
  DISK_ONLY_2   MEMORY_AND_DISK_2   MEMORY_AND_DISK_SER_2   MEMORY_ONLY_2   MEMORY_ONLY_SER_2   OFF_HEAP)
    ```
- Python:
  ```
  from pyspark import storagelevel
  df_events.persist(storagelevel.StorageLevel.MEMORY_ONLY) # or any of the other available levels
  ```
- When using OFF_HEAP for caching, you need additional configuration paramters as in:
  ```
  bin/spark-shell --master local[*] --driver-memory 64g --conf spark.memory.offHeap.enabled=true --conf spark.memory.offHeap.size=64g --jars ../spark-measure_2.11-0.11-SNAPSHOT.jar
  val df = sql("select * from range(1000) cross join range(10000)")
  df.persist(org.apache.spark.storage.StorageLevel.OFF_HEAP)
  ```
---
---
- Spark-root, read high energy physics data in ROOT format into Spark dataframes
  - this is now not maintained, see https://github.com/spark-root/laurelin  
```
in/spark-shell --master local[*] --packages edu.vanderbilt.accre:laurelin:1.1.1 --driver-memory 16g

// input root file
// download from https://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root
val df=spark.read.format("root").option("tree", "Events").load("/home/luca/DoubleMuParked/Run2012BC_DoubleMuParked_Muons.root")


// compact to 1 file
df.coalesce(1).write.mode("overwrite").parquet("/home/luca/DoubleMuParked/Run2012BC_DoubleMuParked_Muons.parquet")
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
  - In addition clients, may want to access the port for the WebUI (4040 by default)
    - configure with `spark.ui.port`  
 
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
df.coalesce(N_partitions).write   // optionally use coalesce if you want to reduce the number of output partitions (beware that it also affects num of concurrent write tasks) 
  .partitionBy(col("colPartition1"), col("colOptionalSubPart")) // partitioning column(s) 
  .bucketBy(numBuckets, "colBucket")   // This feature currently gives error with save, follow SPARK-19256 or use saveAsTable (Hive)
  .format("parquet")
  .save("filePathandName")             // you can use saveAsTable as an alternative

// Options for the write action
.option("parquet.block.size", <blockSize>) // defalut 128MB, see also sc.hadoopConfiguration.setInt("parquet.block.size", <blocksize>
.option("compression", <compression_codec>) // default snappy, see also spark.sql.parquet.compression.codec

// relevant Hadoop configuration parameters:
sc.hadoopConfiguration.setInt("parquet.block.size", .. ) // default to 128 MB parquet block size (size of the column groups)

// relevant Spark configuration parameters:
spark.conf.set("spark.sql.parquet.compression.codec","xxx") // xxx= none, gzip, lzo, snappy, {zstd, brotli, lz4} 
spark.conf.set("spark.sql.files.maxRecordsPerFile", ...) // defaults to 0, use if you need to limit size of files being written  
```
Note a list of options and parameters for the Parquet writer can be found at:  
https://github.com/apache/parquet-mr/blob/master/parquet-hadoop/README.md

// Example with use of savemode:
df.coalesce(4).write.mode(org.apache.spark.sql.SaveMode.Overwrite).parquet("..PATH..")

---
Spark 3.3.0 hidden metadata columns for Parquet reader
```
val df=spark.read.parquet("/tmp/testparquet1")

df.select("_metadata.file_path", "_metadata.file_name","_metadata.file_size", "_metadata.file_modification_time").show(2,false)
```
---
- Repartition / Compact Parquet tables

Parquet table repartition is an operation that you may want to use in the case you ended up with
multiple small files into each partition folder and want to compact them with one file per partition
Example:  
```
val df = spark.read.parquet("myPartitionedTableToCompact")
df.repartition(col("colPartition1"), col("colOptionalSubPartition"))
  .write.partitionBy("colPartition1", "colOptionalSubPartition")
  .format("parquet")
  .save("filePathandName")
```

Note with this you can also sort data withing the partitions, it can be useful for
improving filter execution (for example with Parquet column indexes):  
`.sortWithinPartitions(col("colName"))`

---
- Read from Oracle via JDBC, see more examples at [Spark_Oracle_JDBC_Howto.md](Spark_Oracle_JDBC_Howto.md)
```
val df = spark.read.format("jdbc").
          option("url", "jdbc:oracle:thin:@dbserver:port/service_name").
          option("driver", "oracle.jdbc.driver.OracleDriver").
          option("dbtable", "MYSCHEMA.MYTABLE").
          //option("query", myquery_string).
          option("user", "MYORAUSER").
          option("password", "XXX").
          option("fetchsize",10000).
          load()
         
// test
df.printSchema
df.show(5)
         
// write data as compressed Parquet files  
df.write.parquet("MYHDFS_TARGET_DIR/MYTABLENAME")
```
---
- Configuration to switch back to use datasource V1 (as opposed to use datasource V2). 
  - `spark.sql.sources.useV1SourceList` for Spark 3.2.0, this defaults to `"avro,csv,json,kafka,orc,parquet,text"`

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
 - Examples of DataFrame creation for testing
 ```
// SQL
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

# Python
df = spark.createDataFrame([(1, "event1"), (2,"event2"), (3, "event3")], ("id","name"))
df = spark.createDataFrame([[1, "a string", (1,2,3), ("aa","bb","cc")]],"long_col long, string_col string, array_col array<long>, struct_col struct<col1:string,col2:string,col3:string>")

df.printSchema()
root
 |-- long_col: long (nullable = true)
 |-- string_col: string (nullable = true)
 |-- array_col: array (nullable = true)
 |    |-- element: long (containsNull = true)
 |-- struct_col: struct (nullable = true)
 |    |-- col1: string (nullable = true)
 |    |-- col2: string (nullable = true)
 |    |-- col3: string (nullable = true)

// Scala
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

// using case class
scala> case class myclass(id: Integer, name: String, myArray: Array[Double])
scala> val df=Seq(myclass(1, "aaaa", Array(1.1,2.1,3.1)),myclass(2, "bbbb", Array(4.1,5.1,6.1))).toDF
scala> df..show
+---+----+---------------+
| id|name|        myArray|
+---+----+---------------+
|  1|aaaa|[1.1, 2.1, 3.1]|
|  2|bbbb|[4.1, 5.1, 6.1]|
+---+----+---------------+

// case class with  struct
case class myclass2(id: Integer, name: String)
case class myclass(id: Integer, name: String, myArray: Array[Double], mynested: myclass2)
val df=Seq(myclass(1, "aaaa", Array(1.1,2.1,3.1), myclass2(11, "zzzz")),myclass(2, "bbbb", Array(4.1,5.1,6.1),myclass2(22,"www"))).toDF

df.printSchema
root
 |-- id: integer (nullable = true)
 |-- name: string (nullable = true)
 |-- myArray: array (nullable = true)
 |    |-- element: double (containsNull = false)
 |-- mynested: struct (nullable = true)
 |    |-- id: integer (nullable = true)
 |    |-- name: string (nullable = true)

 df.show
+---+----+---------------+----------+
| id|name|        myArray|  mynested|
+---+----+---------------+----------+
|  1|aaaa|[1.1, 2.1, 3.1]|[11, zzzz]|
|  2|bbbb|[4.1, 5.1, 6.1]| [22, www]|
+---+----+---------------+----------+

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

- Higher order functions and array processing examples
```
# Prepare test data with arrays
# readings from a sensor measuring temperature in Celsius

schema = "id INT, temp_celsius ARRAY<INT>"
t_list = [1,[35, 36, 32, 30, 40, 42, 38]], [2,[31, 32, 34, 55, 56]]

spark.createDataFrame(t_list, schema).createOrReplaceTempView("temp_data")
spark.sql("select * from temp_data").show(10,False)

# Example of array functions
# Take first temperature reading and the max temperature reading

spark.sql("select temp_celsius[0] first_temp_reading, array_max(temp_celsius) max_reading from temp_data").toPandas()

# Array procesing with Spark using "higher order functions" in SQL
# Compute conversion from Fahrenheit from Celsius for an array of temperatures

spark.sql("""
SELECT id, temp_celsius, 
 transform(temp_celsius, t -> ((t * 9) / 5) + 32) as temp_fahrenheit 
  FROM temp_data
""").toPandas()

# Array procesing using Spark higher order functions in SQL
# Filter temperatures > 38C from an array of temperature values

spark.sql("""
SELECT id, temp_celsius, filter(temp_celsius, t -> t > 38) as high 
FROM temp_data
""").show(10,False)

# This demonstrates using the "legacy" SQL functions explode and collect_list 
# the performance is suboptimal, especially for large arrays
# also quite hard to read

spark.sql("""
with exploded_data as (
  select id, explode(temp_celsius) val from temp_data
)
select id, collect_list(val) from exploded_data where val > 38 group by id
""").show(10,False)

# Example of array functions, aggregate (higher orger function) and cardinality

# - aggregate(expr, start, merge, finish) - Applies a binary operator to an initial state and all elements in the array, 
#   and reduces this to a single state. The final state is converted into the final result by applying a finish function.
# - cardinality(expr) - Returns the size of an array or a map. 

spark.sql("""
          SELECT id, aggregate(temp_celsius, 0, (acc, x) -> acc + x,
          acc -> round(acc / cardinality(temp_celsius),1)) as average_temperature
          from temp_data""").show()

```
---
- Load numpy arrays into a Spark Dataframe
  - example load MNIST dataset from keras.datasets 
  - Note, Spark 3.4 has a new feature to load numpy arrays directly into a Spark Dataframe (see note below)
```
$ pyspark --master local[*] --driver-memory 4g 

import tensorflow as tf

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
# normalize features to 0..1
x_train = x_train / 255.0

# flatten 28x28 arrays with images into one array of 784 elements
x_train = x_train.reshape((x_train.shape[0], -1))
data = [(x_train[i].astype(float).tolist(), int(y_train[i])) for i in range(len(y_train))]

from pyspark.sql.types import *
schema = StructType([StructField("features", ArrayType(FloatType())),
                     StructField("labels_raw", LongType())])

# Use this instead if not flattening the 28x28 array
#schema = StructType([StructField("features", ArrayType(ArrayType(FloatType()))),
#                     StructField("labels_raw", LongType())])

# this is slow, only 1 thread used
df = spark.createDataFrame(data, schema)

from pyspark.ml.feature import OneHotEncoderEstimator
encoder = OneHotEncoderEstimator(inputCols=['labels_raw'],outputCols=['labels'],dropLast=False)
model = encoder.fit(df)
df_train = model.transform(df).select("features","labels")

>>> df_train.printSchema()
root
 |-- features: array (nullable = true)
 |    |-- element: float (containsNull = true)
 |-- labels: vector (nullable = true)

####
# test dataset
#####
x_test = x_test / 255.0
data = [(x_test[i].astype(float).tolist(), int(y_test[i])) for i in range(len(y_test))]
df = spark.createDataFrame(data, schema)
model = encoder.fit(df)
df_test = model.transform(df).select("features","labels")
```
---
 - Additional examples of dealing with nested structures in Spark SQL
```
# Python
# Example with structs and arrays
# Inspired from physics datasets

schema = "event LONG, HLT struct<flag1:boolean, flag2:boolean>, muons ARRAY<STRUCT<pt:FLOAT, eta:FLOAT, mass:FLOAT>>"
t_list = [[1000, [True,True] , [[1.1,2.2,1.0], [1.2,2.2,1.0]]], [1001, [True,True], [[1.2,2.3, 1.0],[1.3,2.3, 1.0]]]]

df = spark.createDataFrame(t_list, schema)
df.printSchema()
df.createOrReplaceTempView("particles")

spark.sql("select * from particles").show(10,False)

# display only flag1 and the first muon in the list

spark.sql("select event, HLT.flag1, muons[0] from particles").show(10,False)

# Examples with Maps

schema = "id INT, myKeyValues MAP<INT, INT>"

t_list = [[1000, {1:1, 2:2}], [1001, {1:10, 2:11, 3:12}]]
df = spark.createDataFrame(t_list, schema)
df.createOrReplaceTempView("t1_map")

df.printSchema()
df.show(10,False)

# Higher order functions with maps
spark.sql("SELECT id, transform_values(myKeyValues, (k, v) -> k + v) as mymap_transformed from t1_map").show(10, False)


// Scala

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
- Fun with Spark SQL, FizBuzz
```
sql("""
select case
    when id % 15 = 0 then 'FizzBuzz'
    when id % 3 = 0 then 'Fizz'
    when id % 5 = 0 then 'Buzz'
    else cast(id as string)
    end as FizzBuzz
from range(20)
order by id""").show()
```
---
- Classic join example with parent-child relationship using Departments and Employees tables
 ```
# Create test tables
# Python
emp = spark.createDataFrame([(1, "Emp1", 10), (2,"Emp2", 10), (3, "Emp3", 20)], ("id","name","dep_id"))
dep = spark.createDataFrame([(10, "Department1"), (20, "Department2"), (30, "Department3")], ("id","name"))

// Scala
val emp = Seq((1, "Emp1", 10), (2,"Emp2", 10), (3, "Emp3", 20)).toDF("id","name","dep_id")
val dep = Seq((10, "Department1"), (20, "Department2"), (30, "Department3")).toDF("id","name")

emp.createOrReplaceTempView("employees")
dep.createOrReplaceTempView("departments")

# Inner join
spark.sql("""
select employees.id, employees.name emp_name, departments.name dep_name
from employees join departments
on employees.dep_id = departments.id
order by employees.id""").show()

# Outer join
spark.sql("""
select departments.id, departments.name dep_name, employees.name emp_name
from departments left outer join employees
on employees.dep_id = departments.id
order by departments.id""").show() 
```

Window/analytic functions SQL example: 
```
# Window function
spark.sql("""
select id, name, dep_id,
       max(id) over (partition by dep_id) as greatest_id_same_department,
       lag(name) over (order by id) as previous_employee_name
from employees
order by id
""").show()

# Alternative syntax by explicitly naming windows

spark.sql("""
select id, name, dep_id,
       max(id) over w1 as greatest_id_same_department,
       lag(name) over (order by id) as previous_employee_name
from employees
window w1 as (partition by dep_id),
       w2 as (order by id) 
order by id
""").show()
```

---
- Spark SQL aggregate functions, SQL vs. declarative API

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
Columns count/Frequency histograms with Spark SQL

This uses the width_bucket function:

Frequency histogram, SQL version:

```
min_val = 0.25
max_val = 300
num_bins = 30000

df_with_dimuonmass.createOrReplaceTempView("t1")

histogram_data_SQL = spark.sql(f"""
select
width_bucket(Dimuon_mass, {min_val}, {max_val}, {num_bins}) as bucket,
count(*) as N_events
from t1
where Dimuon_mass between {min_val} and {max_val}
group by bucket 
order by bucket
""")
```

Frequency histogram, declarative API version:

```
min_val = 0.25
max_val = 300
num_bins = 30000
step = (max_val - min_val) / num_bins

histogram_data = ( 
    df_with_dimuonmass
        .where(f"Dimuon_mass between {min_val} and {max_val}")
        .selectExpr(f"width_bucket(Dimuon_mass, {min_val}, {max_val}, {num_bins}) as bucket") 
        .groupBy("bucket")
        .count()
        .orderBy("bucket")
    )

# convert bucket number to the corresponding dimoun mass value
histogram_data = histogram_data.selectExpr(f"{min_val} + (bucket - 1/2) * {step} as value", "count as N_events")
```

Other solutions: 

- See [link to article](http://www.silota.com/docs/recipes/sql-histogram-summary-frequency-distribution.html)

- this is an example developed when Spark SQL did not have width_bucket. Spark shell:
```
sql("select id from range(10)").createOrReplaceTempView("t1")
val df=spark.table("t1")

val maxID = df.select(max('id)).collect()(0)(0)
val minID = df.select(min('id)).collect()(0)(0)
val numBuckets = 3

// debug code
//spark.sql(s"select id, least(floor(round((id-$minID)/($maxID-$minID)*$numBuckets,2)),$numBuckets-1) bucketId from t1").show

spark.sql(s"select count(*) id_count, least(floor(round((id-$minID)/($maxID-$minID)*$numBuckets,2)),$numBuckets-1) bucketId from t1 group by bucketId order by bucketId").show

+--------+--------+
|id_count|bucketId|
+--------+--------+
|       3|       0|
|       3|       1|
|       4|       2|
+--------+--------+

```
- Note that Spark RDD API has a histogram function [see doc](https://spark.apache.org/docs/latest/api/python/pyspark.html)
It can be used with Spark Dataframes as a workaround as in:
```
sql("select cast(id as double) from t1").rdd.map(x => x(0).asInstanceOf[Double]).histogram(3)

res1: (Array[Double], Array[Long]) = (Array(0.0, 3.0, 6.0, 9.0),Array(3, 3, 4))
```

- Time series data bucketing using the function window 
  - it is based on the function [window](https://spark.apache.org/docs/latest/api/sql/index.html#window)
  - this comes from windows for streaming, see also [time windows](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#types-of-time-windows)
  - however are useful for time series processing too, notably for bucketing by timestamp ranges

```
# Generate a DataFrame with toy data for demo purposes
num_events = 100
scale = 100
seed = 4242
start_date = "2022-10-01"

spark.sql(f"""
select id, 
       to_timestamp('{start_date}', 'yyyy-MM-dd') + cast(id as interval minute) as TS,
       random({seed}) * {scale} as random_value
from range({num_events})
""").createOrReplaceTempView("t1")


# Process time series data with group by window on 15-minute intervals
spark.sql("select window.start, window.end, avg(random_value) from t1 group by window(ts, '15 minutes')").show(10, False)

+-------------------+-------------------+------------------+
|start              |end                |avg(random_value) |
+-------------------+-------------------+------------------+
|2022-10-01 00:00:00|2022-10-01 00:15:00|42.55364533764726 |
|2022-10-01 00:15:00|2022-10-01 00:30:00|41.56932036620883 |
|2022-10-01 00:30:00|2022-10-01 00:45:00|54.21355326316869 |
|2022-10-01 00:45:00|2022-10-01 01:00:00|45.49226145897988 |
|2022-10-01 01:00:00|2022-10-01 01:15:00|61.49623581612132 |
|2022-10-01 01:15:00|2022-10-01 01:30:00|47.134134973422185|
|2022-10-01 01:30:00|2022-10-01 01:45:00|58.70822290927983 |
+-------------------+-------------------+------------------+
```
---
Spark binary file format (Spark 3.0)
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
  - Download and build the Spark package from https://github.com/databricks/spark-sql-perf
      - Note for Spark 3 I am currently and temporarily using https://github.com/lucacanali/spark-sql-perf
  - Download and build tpcds-kit for generating data from https://github.com/databricks/tpcds-kit
  - Testing
    1. Generate schema
    2. Run benchmark
    3. Extract results

See instructions at the [spark-sql-perf](https://github.com/databricks/spark-sql-perf) git repo
for additional info on how to generate data and tun the package. Here some pointers/examples:
```
///// 1. Generate schema
bin/spark-shell --master yarn --num-executors 25 --driver-memory 12g --executor-memory 12g --executor-cores 4 --jars <path_here>/spark-sql-perf_2.12-0.5.1-SNAPSHOT.jar

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

bin/spark-shell --master yarn --num-executors 32 --executor-cores 8 --driver-memory 8g --executor-memory 16g --jars /home/luca/spark-sql-perf-new/target/scala-2.11/spark-sql-perf_2.11-0.5.1-SNAPSHOT.jar --conf spark.sql.shuffle.partitions=512 --conf spark.sql.crossJoin.enabled=true --conf spark.eventLog.enabled=false --conf spark.sql.autoBroadcastJoinThreshold=100000000
// when using a large number of cores consider bumping up conf spark.sql.shuffle.partitions (defaiut is 200)
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

--------------------
// Example of how to put exclude list (or similarly use for include lists) to limit number of querries:
//val benchmarkQueries = for (q <- tpcds.tpcds1_4Queries if !q.name.matches("q14a-v1.4|q14b-v1.4|q72-v1.4")) yield(q)
//val experiment = tpcds.runExperiment(benchmarkQueries)

///// 4. Extract results
// simply print execution time results
df.selectExpr("name", "round(executionTime/1000,3) as exec_time_sec").show(1000)

// or use this:
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

////// Eperiment with caching large tables prior to running the benchmak (you need to have enough memory allocated to the executors)

//Tables/views to cache
//val list_tables=List("catalog_returns","inventory","store_sales","store_returns","web_sales","web_returns","call_center","catalog_page","customer","customer_address","customer_demographics","date_dim","household_demographics","income_band","item","promotion","reason","ship_mode","store","time_dim","warehouse","web_page","web_site")
val list_tables=List("catalog_returns","inventory","store_sales","store_returns","web_sales","web_returns","customer")
for (t <- list_tables) spark.table(t).persist(org.apache.spark.storage.StorageLevel.MEMORY_ONLY).count()

```

---
- TPCDS run queries from spark-shell

```
// create the TPCDS schema tables
// this method uses temporary views
val path="/project/spark/TPCDS/tpcds_1500_parquet_1.12.0/"
val tables=List("catalog_returns","catalog_sales","inventory","store_returns","store_sales","web_sales",web_returns","call_center","catalog_page","customer","customer_address","customer_demographics","date_dim","household_demographics","income_band","item","promotion","reason","ship_mode","store","time_dim","warehouse","web_page","web_site")

for (t <- tables) {
println(s"Creating temporary view $t")
spark.read.parquet(path + t).createOrReplaceTempView(t)
}

// defines query/queries you want to use, example
// https://raw.githubusercontent.com/databricks/spark-sql-perf/master/src/main/resources/tpcds_2_4/q3.sql

val q3 = """
SELECT dt.d_year, item.i_brand_id brand_id, item.i_brand brand,SUM(ss_ext_sales_price) sum_agg
FROM  date_dim dt, store_sales, item
WHERE dt.d_date_sk = store_sales.ss_sold_date_sk
  AND store_sales.ss_item_sk = item.i_item_sk
  AND item.i_manufact_id = 128
  AND dt.d_moy=11
GROUP BY dt.d_year, item.i_brand, item.i_brand_id
ORDER BY dt.d_year, sum_agg desc, brand_id
LIMIT 100
"""

// run the query
spark.time(sql(q3).limit(100).collect)
```
---
- Copy TPCDS benchmark data to newer Parquet versions or change compression

Spark 3.2 comes with Parquet 1.12.0, Spark 3.1 with parquet 1.10.1.
If you want to use the new parquet format without recreating the schema, use this:
```
val inpath="/project/spark/TPCDS/tpcds_1500_parquet_1.10.1/"
val outpath="/project/spark/TPCDS/tpcds_1500_parquet_1.12.0/"
//val outpath="/project/spark/TPCDS/tpcds_1500_parquet_1.12.0_zstd/"
//val compression_type="zstd"

val tables_partition=List(("catalog_returns","cr_returned_date_sk"), ("catalog_sales","cs_sold_date_sk"), ("inventory","inv_date_sk"), ("store_returns","sr_returned_date_sk"), ("store_sales","ss_sold_date_sk"), ("web_returns","wr_returned_date_sk"), ("web_sales","ws_sold_date_sk"))
for (t <- tables_partition) {
  println(s"Copying partitioned table $t")
  spark.read.parquet(inpath + t._1).repartition(col(t._2)).write.partitionBy(t._2).mode("overwrite").option("compression", compression_type).parquet(outpath + t._1)
}

val tables_nopartition=List("call_center","catalog_page","customer","customer_address","customer_demographics","date_dim","household_demographics","income_band","item","promotion","reason","ship_mode","store","time_dim","warehouse","web_page","web_site")
for (t <- tables_nopartition) {
  println(s"Copying table $t")
  spark.read.parquet(inpath + t).coalesce(1).write.mode("overwrite").option("compression", compression_type).parquet(outpath + t)
}
```

---
- Generate a simple I/O intensive benchmark load with Spark
  - Setup or copy a large test table, using TPCDS schema
  - query a large fact table, for example store_sales with a filter condition that forces a full scan
  - use the noop data source to write data "to dev/null" as in: `df.write.format("noop").mode("overwrite").save`
  - Previously (Spark 2x) I have used this workaround instead: 
     - Use a filter condition that returns 0 (or very few rows) and use "select *" (all columns)
     - Check the execution plan: you want to confirm that Spark is not using partition pruning nor is managing to push down filters successfully
     - In the following example this is achieved adding a filter condition with a decimal value that has higher precision than the table values
  - Use Spark dashboard and/or sparkMeasure and/or OS tools to make sure the query runs as intended, i.e. performing a full table scan.
  - Example query:
  ```
  val df=spark.read.parquet("/project/spark/TPCDS/tpcds_1500_parquet_1.12.0/store_sales")
  df.write.format("noop").mode("overwrite").save
  // workaround used for Spark 2.x -> df.where("ss_sales_price=37.8688").collect
  
  # SQL version
  df.createOrReplaceTempView("store_sales")
  spark.sql("select * from store_sales").write.format("noop").mode("overwrite").save
  // workaround used for Spark 2.x -> spark.sql("select * from store_sales where ss_sales_price=37.8688").collect
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

This will appear in the sink, for example if you sink to grahite a record:
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
    --packages org.apache.hadoop:hadoop-aws:3.2.0 # edit hadoop-aws version to match Spark's Hadoop

  # example of how to use
  val df=spark.read.parquet("s3a://datasets/tpcds-1g/web_sales")
  df.count
  ```
  - Note, I have noticed that Hadoop 3.2/hadoop-aws 3.2 reading from s3.cern.ch gets stuck when listing 
  directories with a large number of files (as in the TPCDS benchmark). The workaround is to add:
  ```
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
 - How to add a description to a Spark job:
   - spark.sparkContext.setJobDescription("job description")
   - Note: in Spark 3.0, when using Spark SQL/Dataframes: "job description" will be displayed in SQL tab
   - See also: `spark.sparkContext.setJobGroup(groupId: String,description: String,interruptOnCancel: Boolean)`
 
 ---
 Salting SQL joins to work around problems with data skew on large tables, example:
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
---
Collect query results into an array

Python example:
```
>>> spark.sql("select id from range(10)").rdd.map(lambda x: x[0]).collect()
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

Scala example:
```
scala> spark.sql("select id from range(10)").rdd.map(x => x(0)).collect()
res1: Array[Any] = Array(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
```

---
Use Futures on the driver to run multiple DataFrame operations in concurrently
This can be useful when each single operation does not manage to keep all available executor cores busy,
as in the case of skew, long tails, operations that don't parallelize well, as querying RDDBs over JDBC.
  
Scala Futures example:  

```
import scala.concurrent._
import scala.concurrent.duration._
import scala.concurrent.ExecutionContext.Implicits.global


// get the SparkSession, this is intended to be allocated via SparkSubmit already
// use schedule in FAIR mode
val spark = SparkSession.
    builder().
    appName("AtlasDBImport").
    config("spark.scheduler.mode", "FAIR").
    getOrCreate()

// lauch spark actions inside Future
val res1 = Future {
        val df = spark.read....
        df.count
        }

// Run more actions with the same pattern using Future..

// wait for results  to complete
wait.result(res1, 1 hour)
```

Python Futures example:  

```
# process tables extraction concurrently using futures
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        to_do: list[futures.Future] = []

        # this code snippet is taken from a working example
        # submit concurrent execution of table import Spark actions packaged in a procedure
        for table in ImportDetails:
            future = executor.submit(import_from_dbtable_into_parquet, spark, table, args) # run the Spark jobs
            to_do.append(future)
            print(f"Scheduled import of {table['table_name']}: {future}")

        # wait for futures to finish
        for future in futures.as_completed(to_do):
            res: str = future.result()
            print(f"{future} finished. Result: {res}")
```
---
Run spark-shell using the official Spark docker image  
Note currently does not work to pyspark  
`docker run -it apache/spark /opt/spark/bin/spark-shell`

----
Parametrized SQL and 
"bind variables" in Spark
Use the integrated Python string formatter for SQL API in PySpark and Spark Scala API  
From Spark 3.3.0 and improved in Spark 3.4.0. Spark 3.5.0 supports positional parameters in Python sql.
See also [PySpark doc](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.sql.html#pyspark.sql.SparkSession.sql)    
Note this allows to use a dataframe in SQL without explicitly registering it as temporary view  

Python example:
```
# parametrized SQL
>>> spark.sql("select 1, :aa", {"aa" : 7}).show()
+---+---+
|  1|  7|
+---+---+
|  1|  7|
+---+---+

# String formatter substitution
>>> spark.sql("select 1, {aa}", aa=7).show()
+---+---+
|  1|  7|
+---+---+
|  1|  7|
+---+---+

spark.sql("SELECT * FROM range(10) WHERE id > {bound1} AND id < {bound2}", bound1=2, bound2=4).show()

# Positional parameters example in Python SQL (from Spark 3.5.0)  
mydf=spark.sql("select id a, id+1 b from range(10)")
spark.sql("SELECT * FROM {df} WHERE {df[B]} > ? and ? < {df[A]}", args=[5, 2], df=mydf).show()

---
# use DF in SQL without the need to register it as a temp table
df = spark.sql("select id from range(10)")
spark.sql("select 1 from {aa}", aa=df).show()

mydf = spark.range(10)
spark.sql("select id, {col} from {tbl}", tbl=mydf, col=mydf.id).show()

# more complex example, from the Spark doc
spark.sql('''
  SELECT m1.a, m2.b
  FROM {table1} m1 INNER JOIN {table2} m2
  ON m1.key = m2.key
  ORDER BY m1.a, m2.b''',
  table1=spark.createDataFrame([(1, "a"), (2, "b")], ["a", "key"]),
  table2=spark.createDataFrame([(3, "a"), (4, "b"), (5, "b")], ["b", "key"])).show()
```

Scala example - parametrized SQL:
```
spark.sql("select 1, :aa",Map("aa" -> 7)).show()

scala> spark.sql("select 1, :aa",Map("aa" -> 7)).show()
+---+---+
|  1|  7|
+---+---+
|  1|  7|
+---+---+
```

---
PySpark UDF profiler  
See: https://issues.apache.org/jira/browse/SPARK-37443  
```
bin/pyspark --conf spark.python.profile=true

from pyspark.sql.functions import udf
df = spark.range(10)

@udf("long")
def add1(x):
   return x + 1

@udf("long")
def add2(x):
   return x + 2

added = df.select(add1("id"), add2("id"), add1("id"))
added.show()
added.explain()

sc.show_profiles()
```
----
Helper code/query for splitting a large table in multiple disjoint table chunks of equal size.   
By using approx_percentile, this works relatively fast with large table and high-cardinality columns.  

```
// test the idea with this toy code:
val df = spark.range(100)
df.selectExpr("approx_percentile(id, array(0.25, 0.5, 0.75))").show()

// A more realistic example would be more something like this:

val df = spark.read.parquet("<PATH>/myLargeTable.parquet")
// compute the approximate percentile at multiple point, they will provide the "split points" for filtering the table
// In this example the provided 3 percentile allow to split the table in 4 chunks having very similar number of rows
df.selectExpr("approx_percentile(<col_to_use>, array(0.25, 0.5, 0.75), 10)").show()
```
---
From spark-shell:  
`spark.sessionState.conf. <tab>` ->  to see list configurations and query parameter

---
Spark 3.4 and numpy  
New feature to create dataframes from numpy arrays

```
import tensorflow as tf
import numpy as np

mnist = np.load("/home/luca/.keras/datasets/mnist.npz")
(x_train, y_train), (x_test, y_test) = (mnist['x_train'], mnist['y_train']), (mnist['x_test'], mnist['y_test'])

>>> x_test.shape
(10000, 28, 28)

x_test2=x_test.reshape(10000,28*28)

# this is slow and serially executed (1 core)
df=spark.createDataFrame(x_test2)

the result is a df with 784 columns
```
