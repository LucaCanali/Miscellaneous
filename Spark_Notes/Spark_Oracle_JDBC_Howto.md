# Notes on querying Oracle from Apache Spark. 

Relevant to reading Oracle tables using Spark SQl (Dataframes API), to transfer data from
Oracle into Parquet or other formats.
Find here also some notes on measuring performance, use of partitioning and also some thoughts on Apache Sqoop vs. Spark for data transfer.   
   
#### An example of how to create a Spark DataFrame that reads from and Oracle table/view/query using JDBC.
See also [Spark documentation]()https://spark.apache.org/docs/latest/sql-programming-guide.html#jdbc-to-other-databases)

```
# You need an Oracle client JDBC jar, available for download from the Oracle website
# This example uses ojdb8.jar from Oracle 12.2 client, older versions such as ojdbc6.jar work OK too
bin/spark-shell --jars oracle_client/instantclient_12_2/ojdbc8.jar

val df = spark.read.format("jdbc")
         .option("url", "jdbc:oracle:thin:@dbserver:port/service_name")
         .option("driver", "oracle.jdbc.driver.OracleDriver")
         .option("dbtable", "MYSCHEMA.MYTABLE")
         .option("user", "MYORAUSER")
         .option("password", "XXX")
         .option("fetchsize",10000)
         .load()
         
// test
df.printSchema
df.show(5)
         
// write Spark data frame as (snappy compressed) Parquet files  
df.write.parquet("MYHDFS_TARGET_DIR/MYTABLENAME")
```
```
// Similar to above, alternative syntax
val connectionProperties = new java.util.Properties()
connectionProperties.put("user", "MYORAUSER)
connectionProperties.put("password", "XXX")

val df = spark.read.option("driver","oracle.jdbc.driver.OracleDriver").option("fetchsize",1000)
         .jdbc("jdbc:oracle:thin:@dbserver:port/service_name", "MYSCHEMA.MYTABLE", connectionProperties )
```


```
# alternative syntax to read from Oracle using Spark SQL
sql(s"""
  |CREATE OR REPLACE TEMPORARY VIEW mySparkTempView
  |USING org.apache.spark.sql.jdbc
  |OPTIONS (url 'jdbc:oracle:thin:@dbserver:port/service_name',
  |driver 'oracle.jdbc.driver.OracleDriver',
  |user 'MYORAUSER', password 'XXX',
  |fetchsize 10000,
  |dbtable 'MYSCHEMA.MYTABLE')
  """.stripMargin)

sql("select * from mySparkTempView").show(5)
```

### Examples on how to write to Oracle
```
import org.apache.spark.sql.SaveMode

df.write.mode(SaveMode.Append).format("jdbc")
        .option("driver", "oracle.jdbc.driver.OracleDriver")
        .option("url", "jdbc:oracle:thin:@dbserver:port/service_name")
        .option("dbtable", "MYSCHEMA.MYTABLE")
        .option("user", "MYORAUSER")
        .option("password", "XXX")
        .save()

val connectionProperties = new java.util.Properties()
connectionProperties.put("user", "MYORAUSER)
connectionProperties.put("password", "XXX")
df.write.mode(SaveMode.Append)
        .option("driver", "oracle.jdbc.driver.OracleDriver")
        .jdbc("jdbc:oracle:thin:@dbserver:port/service_name", "MYSCHEMA.MYTABLE", connectionProperties )

```

### Example with TPCS protocol
Tested with Oracle 18c
```
bin/spark-shell --jars <path>/ojdbc8.jar

val connectionProperties = new java.util.Properties()
connectionProperties.put("user", "MYUSER")
connectionProperties.put("password", "MYPASS")
connectionProperties.put("javax.net.ssl.trustStore","<path>/keystore.jks")
//connectionProperties.put("javax.net.ssl.trustStoreType","JKS")
connectionProperties.put("javax.net.ssl.trustStorePassword","MyKeystorPassword")

val df = spark.read.format("jdbc").option("driver","oracle.jdbc.driver.OracleDriver")
              .option("fetchsize",1000)
              .jdbc("jdbc:oracle:thin:@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=tcps)(HOST=hostname)(PORT=TPCDS_port)))(CONNECT_DATA=(SERVICE_NAME=orcl.cern.ch)))", "MYSCHEMA.MYTABLE", connectionProperties )

```

#### Note on partitioning/parallelization of the JDBC source with Spark:

- The instruction above will read from Oracle using a single Spark task, this can be slow. 
- When using partitioning options Spark will use as many tasks as "numPartitions" 
- Each task will issue a query to read the data with an additional "where condition" generated from the lower and upper bounds and the number of partitions.
- If the Oracle table is partitioned by the column "partitionColumn" this could improve performance and use partition pruning
 for example.
 In other cases the query can generate multiple table scans or suboptimal index range scans of large parts of the table.
 See also below the discussion on Sqoop, that has additional optimizations for mappers/partitioners to use with Oracle.
 This functionality has not yet been ported to Spark.
- When loading large tables you may want to check with a DBA that the load is acceptable on the source DB
Example:

```
       .option("partitionColumn","JOBID")
       .option("lowerBound",0)
       .option("upperBound",420000000)
       .option("numPartitions",12)
```

Note: instead of a table name you can specify a query as in 
```
       .option("dbtable", "(select * from MYSCHEMA.MYTABLE where rownum<=20)")
```
---
   
#### What to check on the Oracle side and what to expect

- Use an Oracle monitoring tool, such as Oracle EM, or use relevant ["DBA scripts" as in this repo](https://github.com/LucaCanali/Oracle_DBA_scripts) 
- Check the number of sessions connected to Oracle from the Spark executors and the sql_id of the SQL they are executing.
  - expect numPartitions sessions in Oracle (1 session if you did not specify the option)   
  - The relevant info is in V$SESSION, or use the script ```@sessinfo s.username='MYORAUSER'```
- Drill down on the SQL being executed
  - from the sql_id see the SQl text from V$SQLSTATS or use the script ```@sql <sql_id>```
  - you should see queries on the table you specified, optionally with where caluses to read chunks of it if you sepficied partitioning cluases
- Check the load on the DB server 
  - this can be done from Oralce SQL using V$SYSMETRIC or the script ```@sysmetric```
  - See various OS and DB metrics, including the network throughput
  - You should expect the network throughput by this additional load to be around 10MB/sec per session. It could be less if reading from tables with small rows.
- Check Oracle active sessions and wait events 
  - query from V$SESSION and V$EVENTMETRIC to see the workload, for example use the scripts ```@top and @eventmetric``` 
  - in many cases you may see a low load on Oracle
  - for example if workload is reading from Oracle and writing into Parquet, you'll find that in many cases the bottleneck is the CPU needed by Spark tasks to write into Parquet
  - when the bottleneck is on the Spark side, Oracle sessions will report "wait events" such as: "SQL*Net more data to client", measning that Oracle sessions are waiting to be able to push more data to Spark executors which are otherwise busy 
  
#### What to check on the Spark side
- Check the SPARK UI to see the progress of the job and how many tasks are being used concurrently
  - you should expect "numPartitions" tasks (1 tasks if you did not specify a value for this option)
- measure the workload with [sparkMeasure as described in this doc](Spark_Performace_Tool_sparkMeasure.md)
```
bin/spark-shell --jars oracle_client/instantclient_12_2/ojdbc8.jar --packages ch.cern.sparkmeasure:spark-measure_2.11:0.11

val stageMetrics = ch.cern.sparkmeasure.StageMetrics(spark) 
stageMetrics.runAndMeasure(spark.df.write.parquet("MYHDFS_TARGET_DIR/MYTABLENAME")
```
For example the output from a run with parallelism 12 shows that most of the time was spent running CPU cycles on the Spark cluster (rather than on Oracle which was mostly idle):
```
Scheduling mode = FIFO
Spark Context default degree of parallelism = 12
Aggregated Spark stage metrics:
numStages => 1
sum(numTasks) => 12
elapsedTime => 1140904 (19 min)
sum(stageDuration) => 1140904 (19 min)
sum(executorRunTime) => 10118202 (2.8 h)
sum(executorCpuTime) => 9660645 (2.7 h)
sum(executorDeserializeTime) => 4058 (4 s)
sum(executorDeserializeCpuTime) => 3520 (4 s)
sum(resultSerializationTime) => 31 (31 ms)
sum(jvmGCTime) => 150127 (2.5 min)
sum(shuffleFetchWaitTime) => 0 (0 ms)
sum(shuffleWriteTime) => 0 (0 ms)
max(resultSize) => 28392 (27.0 KB)
sum(numUpdatedBlockStatuses) => 24
sum(diskBytesSpilled) => 0 (0 Bytes)
sum(memoryBytesSpilled) => 0 (0 Bytes)
max(peakExecutionMemory) => 0
sum(recordsRead) => 815956407
sum(bytesRead) => 0 (0 Bytes)
sum(recordsWritten) => 0
sum(bytesWritten) => 0 (0 Bytes)
sum(shuffleTotalBytesRead) => 0 (0 Bytes)
sum(shuffleTotalBlocksFetched) => 0
sum(shuffleLocalBlocksFetched) => 0
sum(shuffleRemoteBlocksFetched) => 0
sum(shuffleBytesWritten) => 0 (0 Bytes)
sum(shuffleRecordsWritten) => 0

Aggregated Spark accumulables of type internal.metric. Sum of values grouped by metric name
Name => sum(value) [group by name]

executorCpuTime => 9660645 (2.7 h)
executorDeserializeCpuTime => 3520 (4 s)
executorDeserializeTime => 4058 (4 s)
executorRunTime => 10118202 (2.8 h)
input.recordsRead => 815956407
jvmGCTime => 150127 (2.5 min)
resultSerializationTime => 31 (31 ms)
resultSize => 28392 (27.0 KB)

SQL Metrics and other non-internal metrics. Values grouped per accumulatorId and metric name.
Accid, Name => max(value) [group by accId, name]

    0, duration total => 10092211 (2.8 h)
    1, number of output rows => 815956407
```
---
## Notes on Apache Sqoop

Apache Sqoop and in particular its Oracle connector orahoop have additional optimizations
that can improve substantially the performance of data transfer from Oracle to Hadoop compared to the
method described above using Spark.
See [this link to Scoop documentation](http://sqoop.apache.org/docs/1.4.6/SqoopUserGuide.html#_data_connector_for_oracle_and_hadoop)

An example of Sqoop/orahoop usage:

```
sqoop import \
--connect jdbc:oracle:thin:@dbserver:port/service_name \
--username MYORAUSER \
--direct \
--fetch-size 10000 \
-P \
--num-mappers 12 \
--target-dir MYHDFS_TARGET_DIR/MYTABLENAME \
--table "MYSCHEMA.MYTABLE" \
--map-column-java FILEID=Integer,JOBID=Integer,CREATIONDATE=String,INSERTTIMESTAMP=String \
--compress --compression-codec snappy \
--as-parquetfile
```

Notes:
- Sqoop will generate a Map reduce job to process the data transfer
- Compared to the JDBC method with Spark described above this has several optimizations for Oracle
- Notably the way data is split among mappers uses methods that are native for Oracle (ROWID ranges by default, Sqoop can also use Oracle partitions to chunk data with the option -Doraoop.chunk.method="PARTITION"). 
Also data reads for Sqoop workloads by default do not interfere with the Oracle buffer cache (i.e. Sqoop uses serial direct reads).

Issues and remarks:  
- In one system the I found the following blocking Oracle error while loading a DF from an Oracle table with timestamp columns
  ```java.sql.SQLException: ORA-00604: error occurred at recursive SQL level 1
   ORA-01882: timezone region not found
  ```
  This is due to the client configuration and can be fixed by setting the TZ environment to a valid time zone value as in:  
 ```export TZ=CEST```
 
---
## SPARK-21519: Add an option to the JDBC data source to initialize the environment of the remote database session 

[SPARK-21519](https://issues.apache.org/jira/browse/SPARK-21519) introduced an option to the JDBC datasource, "sessionInitStatement" to implement the functionality of session initialization present for example in the Sqoop connector for Oracle (see https://sqoop.apache.org/docs/1.4.6/SqoopUserGuide.html#_oraoop_oracle_session_initialization_statements).   
After each database session is opened to the remote DB, and before starting to read data, this option executes a custom SQL statement (or a PL/SQL block in the case of Oracle).
Example of usage, relevant to Oracle JDBC:

```
bin/spark-shell --jars ojdb6.jar

val preambleSQL="""
begin 
  execute immediate 'alter session set tracefile_identifier=sparkora'; 
  execute immediate 'alter session set "_serial_direct_read"=true';
  execute immediate 'alter session set time_zone=''+02:00''';
end;

val df = spark.read
           .format("jdbc")
           .option("url", "jdbc:oracle:thin:@ORACLEDBSERVER:1521/service_name")
           .option("driver", "oracle.jdbc.driver.OracleDriver")
           .option("dbtable", "(select 1, sysdate, systimestamp, current_timestamp, localtimestamp from dual)")
           .option("user", "MYUSER")
           .option("password", "MYPASSWORK")
           .option("fetchsize",1000)
           .option("sessionInitStatement", preambleSQL)
           .load()

df.show(5,false)
```

Comments: The proposal of this option comes from the need to use it for an Oracle database and enable serial direct read (this allows Oracle to perform read operations that bypass the buffer cache), however it can be used for other DBs too as it is quite generic. Note this mechanism allows to inject code into the database connection, this is not a security vulnerability as it requires password authentication, however beware of the possibilities for injecting SQL (and PL/SQL) that this opens.
