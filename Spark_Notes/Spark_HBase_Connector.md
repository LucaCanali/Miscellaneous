# Apache Spark-HBase Connector

## How to use Spark to access HBase

Spark needs a connector library to access HBase.  
Two connectors are available, which one should you use?
  - **[Apache HBase-Spark connector](https://github.com/apache/hbase-connectors)** 
    - This is  part of the Apache HBase-Spark
  - **[Hortonworks Spark-HBase connector](https://github.com/hortonworks-spark/shc)**
    - The Hortonworks connector has been quite popular over the years, with Spark 2.x.
      However, it appears to be no more supported nor updated?


### Configuration and setup
  - Client-side (Spark) configuration
    - You need the HBase client configuration file `hbase-site.xml` 
    - This points to the HBase you want to connect to  
    - Copy `hbase-site.xml` to `SPARK_CONF_DIR` (default is $SPARK_HOME/conf`)
  - Serve-side (Hbase region servers) configuration 
    - When using the Apache Hbase-Spark connector there is also a server-side configuration
  - 

----
## Spark 2.x
### Spark 2.4 and the Spark-HBase Hortonworks connector
  - The connector for Spark 2.4 is available in Maven Central
  - You need also the configuration steps, see above "Configuration and setup"
  - See additional details: 
    - [Hortonworks Spark-HBase connector on Github](https://github.com/hortonworks-spark/shc)
    - [note on using HBC HBase with Spark 2.4](https://docs.microsoft.com/en-us/azure/hdinsight/hdinsight-using-spark-query-hbase)

  ```
  # Example of how to use the connector with Spark (note: need hbase-site.xml in SPARK_CONF_DIR) 
  bin/spark-shell --master yarn --num-executors 1 --executor-cores 2 \
  --repositories http://repo.hortonworks.com/content/groups/public/ \
  --packages com.hortonworks.shc:shc-core:1.1.0.3.1.2.2-1 
  ```
  ```
  // Example of how to use the Hortonworks connector to read into a DataFrame
  import org.apache.spark.sql.execution.datasources.hbase.HBaseTableCatalog

  val catalog = s"""{
    |"table":{"namespace":"default", "name":"testspark"},
    |"rowkey":"key",
    |"columns":{
    |"id":{"col":"key", "type":"int"},
    |"name":{"cf":"cf", "col":"name", "type":"string"}
    |}
    |}""".stripMargin

  val df = spark.read.options(Map(HBaseTableCatalog.tableCatalog->catalog)).format("org.apache.spark.sql.execution.datasources.hbase").option("hbase.spark.use.hbasecontext", false).load()

  df.show()
 ```

### Spark 2.x and the Apache Spark HBase connector 
  - The connector for Spark 2.x is available in Maven Central
  - You need the configuration steps, see above "Configuration and setup"
    - Note that you need to configure the server-side too

  ```
  # Example of how to use the connector with Spark 
  # Note: you need hbase-site.xml in SPARK_CONF_DIR
  # Note: you need to set up the server-side component too for filter pushdown
  bin/spark-shell --master yarn --num-executors 1 --executor-cores 2 \
  --repositories https://repository.cloudera.com/artifactory/libs-release-local \
  --packages org.apache.hbase.connectors.spark:hbase-spark-protocol-shaded:1.0.0.7.2.2.2-1,org.apache.hbase.connectors.spark:hbase-spark:1.0.0.7.2.2.2-1,org.apache.hbase:hbase-shaded-mapreduce:2.2.4
  ```

  ```
  // Example of how to use the Apache Hbase-Spark connector to read into a DataFrame
  import org.apache.hadoop.hbase.spark.datasources.HBaseTableCatalog
  
  val catalog = s"""{
    |"table":{"namespace":"default", "name":"testspark"},
    |"rowkey":"key",
    |"columns":{
    |"id":{"col":"key", "type":"int"},
    |"name":{"cf":"cf", "col":"name", "type":"string"}
    |}
    |}""".stripMargin

  val df = spark.read.options(Map(HBaseTableCatalog.tableCatalog->catalog)).format("org.apache.hadoop.hbase.spark").option("hbase.spark.use.hbasecontext", false).load()
  // alternative, more compact, syntax for HBase catalog
  // val df = spark.read.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.table", "testspark").option("hbase.spark.use.hbasecontext", false).load()

  df.show()
 ```

----
## Spark 3.x

###  Use the Apache Spark HBase connector with Spark 3.x
- Build the connector from the [github repo Apache HBase Connectors](https://github.com/apache/hbase-connectors)
  - The connector has to be compiled from source for Spark 3.x, as 
  Spark 3.x does not support Scala 2.11, see also [HBASE-25326 Allow hbase-connector to be used with Apache Spark 3.0 ](https://issues.apache.org/jira/browse/HBASE-25326)
  - As of November 2021, the release of hbase-connectors in maven central is compiled with scala 2.11   
  
- Build as in this example (customize HBase, Spark and Hadoop versions, as needed):  
   ```
   mvn -Dspark.version=3.2.0 -Dscala.version=2.12.15 -Dscala.binary.version=2.12 -Dhbase.version=2.3.7 -Dhadoop.profile=3.0 -Dhadoop-three.version=3.3.1 -DskipTests clean package
   ```
   
- Deploy using Spark 3.x, as in this example:
  ```
  # Customize the JARs path to your filesystem location
  # For convenience I have also uploaded the jars on a web server
  JAR1=https://cern.ch/canali/res/hbase-spark-protocol-shaded-1.0.1_spark-3.2.0-hbase-2.3.7-cern1_1.jar
  JAR2=https://cern.ch/canali/res/hbase-spark-1.0.1_spark-3.2.0-hbase-2.3.7-cern1_1.jar

  bin/spark-shell --master yarn --num-executors 1 --executor-cores 2 \
  --jars $JAR1,$JAR2 --packages org.apache.hbase:hbase-shaded-mapreduce:2.3.7
  ```

- Other option, for **CERN users only**: 
  - deploy from artifactory.cern.ch (only visible from CERN network):
  - `bin/spark-shell --master yarn --num-executors 1 --executor-memory 8g --repositories https://artifactory.cern.ch/beco-thirdparty-local --packages org.apache.hbase.connectors.spark:hbase-spark:1.0.1_spark-3.2.0-hbase-2.3.7-cern1_1`

---
## How to run a test workload of Spark writing and reading from HBase using the Spark-Hbase connector:

### Spark-HBase connector: write and read example 

- On HBase, create the test table and grant the related privileges to your user (use `hbase shell`):
  ```
  create 'testspark', 'cf'
  grant '<your_username_here>', 'XRW', 'testspark'
  ```
  - Note this may be too needed: `grant '<your_username_here>', 'X', 'hbase:meta'`
 
- On Spark:
  - Start Spark 2.x or 3.x as detailed above
  - Write:
  ```  
  val df = sql("select id, 'myline_'||id  name from range(10)")
  df.write.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.namespace", "default").option("hbase.table", "testspark").option("hbase.spark.use.hbasecontext", false).save()
  ```
  
- Read back from Spark
  ``` 
  val df = spark.read.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.table", "testspark").option("hbase.spark.use.hbasecontext", false).load()
  df.show()
  ```

- Read back from Spark using a filter, without server-side installation for SQL filter pushdown [HBASE-22769](https://issues.apache.org/jira/browse/HBASE-22769)
  ``` 
  val df = spark.read.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.table", "testspark").option("hbase.spark.use.hbasecontext", false).option("hbase.spark.pushdown.columnfilter", false).load()
  df.show()
  ```

### SQL Filter pushdown and server-side jar configuration

- This allows to push down filter predicates to HBase
  - It is configured with `.option("hbase.spark.pushdown.columnfilter", true)` which is the default. 
  - This requires additional configuration on the HBase server side, in particular one needs to have
    a few jars in the HBase region servers CLASSPATH: scala-library, hbase-spark and hbase-spark-protocol-shaded.
   
- Server-side binaries compile with Scala 2.12 and Spark 3.x:
  - Build the connector from GitHub as explained above or use the prebuilt jars: 
    ```
    JAR1=https://cern.ch/canali/res/hbase-spark-protocol-shaded-1.0.1_spark-3.2.0-hbase-2.3.7-cern1_1.jar
    JAR2=https://cern.ch/canali/res/hbase-spark-1.0.1_spark-3.2.0-hbase-2.3.7-cern1_1.jar
    wget $JAR1 $JAR2
    wget https://repo1.maven.org/maven2/org/scala-lang/scala-library/2.12.15/scala-library-2.12.15.jar
  - ```
- Server-side binaries compile with Scala 2.11 and Spark 2.x:
    - download from maven central:
    ```
    scala-library-2.11.12.jar
    hbase-spark-1.0.0.jar
    hbase-spark-protocol-shaded-1.0.0.jar
    ```

  - If this is not set you will get
  an error: `java.lang.NoClassDefFoundError: org/apache/hadoop/hbase/spark/datasources/JavaBytesEncoder$`
    - See: [HBASE-22769](https://issues.apache.org/jira/browse/HBASE-22769)  
    - Example of how to use SQL filter pushdown
  ``` 
  val df = spark.read.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.table", "testspark").option("hbase.spark.use.hbasecontext", false).option("hbase.spark.pushdown.columnfilter", true).load()
  df.filter("id==9").show()
  ```
  
----
### Another option for writing and reading by explicitly specifying the catalog in JSON format
  - see also [HbaseTableCatalog](https://github.com/apache/hbase-connectors/blob/master/spark/hbase-spark/src/main/scala/org/apache/hadoop/hbase/spark/datasources/HBaseTableCatalog.scala)

- On HBase, grant create table privilege to your user:
  ```
  grant '<your_username_here>', 'C'
  ```
- On Spark:
  - Start Spark 2.x or 3.x as detailed above

  - Write:  
  ```
  import org.apache.hadoop.hbase.spark.datasources.HBaseTableCatalog

  val catalog = s"""{
    |"table":{"namespace":"default", "name":"testspark"},
    |"rowkey":"key",
    |"columns":{
    |"id":{"col":"key", "type":"int"},
    |"name":{"cf":"cf", "col":"name", "type":"string"}
    |}
    |}""".stripMargin

  val df = sql("select id, 'myline_'||id  name from range(10)")

  // HBaseTableCatalog.newTable -> If defined and larger than 3, a new table will be created with the number of region specified.
  df.write.options(Map(HBaseTableCatalog.tableCatalog->catalog, HBaseTableCatalog.newTable -> "5")).format("org.apache.hadoop.hbase.spark").option("hbase.spark.use.hbasecontext", false).save()
  ```

- Read HBase from Spark
  ```
  import org.apache.hadoop.hbase.spark.datasources.HBaseTableCatalog

  val catalog = s"""{
    |"table":{"namespace":"default", "name":"testspark"},
    |"rowkey":"key",
    |"columns":{
    |"id":{"col":"key", "type":"int"},
    |"name":{"cf":"cf", "col":"name", "type":"string"}
    |}
    |}""".stripMargin

  val df = spark.read.options(Map(HBaseTableCatalog.tableCatalog->catalog)).format("org.apache.hadoop.hbase.spark").option("hbase.spark.use.hbasecontext", false).load()
  df.show()
  ```
  
### PySpark

- Note: this is almost the same as with Scala examples above,
with the important change of substituting spark-shell with pyspark  
  
- See above for "Configuration and setup" how to configure Hbase client and server.

- Spark 3.x (see details above in "Spark 3.x and the Apache Spark HBase connector")
  ```
  bin/pyspark --master yarn --num-executors 2 --executor-cores 2 \
   --jars $JAR1,$JAR2 --packages org.apache.hbase:hbase-shaded-mapreduce:2.3.7
  ```
  
- Spark 2.x
  ```
   bin/pyspark --master yarn --num-executors 1 --executor-cores 2 \
  --repositories https://repository.cloudera.com/artifactory/libs-release-local \
  --packages org.apache.hbase.connectors.spark:hbase-spark-protocol-shaded:1.0.0.7.2.2.2-1,org.apache.hbase.connectors.spark:hbase-spark:1.0.0.7.2.2.2-1,org.apache.hbase:hbase-shaded-mapreduce:2.2.4
  ```
  
- Write
  ```  
  df = spark.sql("select id, 'myline_'||id  name from range(10)")
  df.write.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.namespace", "default").option("hbase.table", "testspark").option("hbase.spark.use.hbasecontext", False).save()
  ```

- Read HBase from Spark

  ```
  df = spark.read.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.table", "testspark").option("hbase.spark.use.hbasecontext", False).load()
  df.show()
  df.filter("id<10").show() # see above note on SQL filter pushdown server-side configuration
  ```
  
- Another option for reading: explicitly specify the catalog in JSON format:
  ```
  import json

  catalog = json.dumps(
    {
        "table":{"namespace":"default", "name":"testspark"},
        "rowkey":"key",
        "columns":{
            "id":{"col":"key", "type":"int"},
            "name":{"cf":"cf", "col":"name", "type":"string"}
        }
    })

  df = spark.read.options(catalog=catalog).format("org.apache.hadoop.hbase.spark").option("hbase.spark.use.hbasecontext", False).load()
  
  df.show()
  ```
