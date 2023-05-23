# Apache Spark-HBase Connector

## How to use Spark to access HBase

Apache Spark needs a connector library to access HBase.  
Two connectors Spark-HBase are available, which one should you use?
  - **[Apache HBase-Spark connector](https://github.com/apache/hbase-connectors)** 
    - This is  part of the Apache HBase-Spark
  - **[Hortonworks Spark-HBase connector](https://github.com/hortonworks-spark/shc)**
    - The Hortonworks connector has been quite popular over the years, with Spark 2.x.
      However, it appears to be no more supported nor updated?

## Note on Apache Phoenix connector for Spark:
  - [Apache Phoenix](https://phoenix.apache.org/)
    - Apache Phoenix and its connector for Apache Spark provide another (alternative) way to access HBase from Spark    
    - Phoenix is an extra layer on top of HBase, which can simplify SQL-based access to HBase tables
    - Phoenix needs server-side installation and configuration, see documentation
    - A Spark connector for Apache Phoenix is available, see [phoenix-connectors](https://github.com/apache/phoenix-connectors)
      - The connector for Spark 2.x is available on maven central
      - For Spark 3.x, I used the connector compiled from source (as of May 2023).
        - Notes on the build: `mvn package -Dhbase-two.version=2.4.17 -Dhadoop-three-version=3.3.4 -DskipTests`
      I have uploaded the JAR to a web page, this is an example of how to use it with Spark 3:
       ```
      JAR=http://canali.web.cern.ch/res/phoenix5-spark3-shaded-6.0.0-SNAPSHOT.jar 
      spark-shell --jars $JAR --packages org.apache.hbase:hbase-shaded-mapreduce:2.4.17
      
      val df=spark.read.format("org.apache.phoenix.spark").option("table", "TABLE_NAME").option("zkUrl", "zookeeper_url:2181").load()
      ```

---
## Spark-HBase connector configuration and setup
**Client-side** (Spark) configuration:
  - You need the HBase client configuration file `hbase-site.xml` 
  - This points to the HBase you want to connect to  
  - Copy `hbase-site.xml` to `SPARK_CONF_DIR` (default is $SPARK_HOME/conf`)
  
**Server-side** (HBase region servers) configuration:   
  - This is only needed for the Apache HBase-Spark connector
  - It requires additional configuration on the HBase server side, in particular one needs to have
    a few jars in the HBase region servers CLASSPATH (for example copy it to /usr/hdp/hbase-2.3/lib: 
    - scala-library
    - hbase-spark
    - hbase-spark-protocol-shaded.
  - Build the connector from GitHub as explained below (see Spark 3.x section). 
    In this example we use pre-built jars JAR1 and JAR2.
    ```
    # Download connector jars to HBase region servers $HBASE_HOME/lib
    # Stopgap, files served from my homepage

    wget http://canali.web.cern.ch/res/hbase-spark-1.0.1-SNAPSHOT_spark331_hbase2415.jar
    wget http://canali.web.cern.ch/res/hbase-spark-protocol-shaded-1.0.1-SNAPSHOT_spark331_hbase2415.jar
    
    # Scala library, match the Scala version used for building
    wget https://repo1.maven.org/maven2/org/scala-lang/scala-library/2.12.15/scala-library-2.12.15.jar
    ```
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
- Build the connector from the GitHub repo [Apache HBase Connectors](https://github.com/apache/hbase-connectors)
  - As of December 2022, the hbase-connectors releases in maven central are only available for Scala 2.11 and cannot be used with Spark 3.x
  - The connector has to be compiled from source for Spark 3.x, see also [HBASE-25326 Allow hbase-connector to be used with Apache Spark 3.0 ](https://issues.apache.org/jira/browse/HBASE-25326)
  
- Build as in this example (customize HBase, Spark and Hadoop versions, as needed):
   ```
   mvn -Dspark.version=3.3.1 -Dscala.version=2.12.15 -Dscala.binary.version=2.12 -Dhbase.version=2.4.15 -Dhadoop-three.version=3.3.2 -DskipTests clean package
   ```
   
- Deploy using Spark 3.x, as in this example:
  ```
  # Build from source or use the pre-compiled JARs
  # Stopgap, files served from my homepage
  JAR1=http://canali.web.cern.ch/res/hbase-spark-1.0.1-SNAPSHOT_spark331_hbase2415.jar
  JAR2=http://canali.web.cern.ch/res/hbase-spark-protocol-shaded-1.0.1-SNAPSHOT_spark331_hbase2415.jar

  bin/spark-shell --master yarn --num-executors 1 --executor-cores 2 \
  --jars $JAR1,$JAR2 --packages org.apache.hbase:hbase-shaded-mapreduce:2.4.15
  ```

### SQL Filter pushdown and server-side library configuration

- This allows to push down filter predicates to HBase
  - It is configured with `.option("hbase.spark.pushdown.columnfilter", true)` which is the default. 
  - This requires additional configuration on the HBase server side, in particular one needs to have
    a few jars in the HBase region servers CLASSPATH: scala-library, hbase-spark and hbase-spark-protocol-shaded.
  - See "Configuration and setup" section for details
  - If filter pushdown jars are not configured you will get
  an error: `java.lang.NoClassDefFoundError: org/apache/hadoop/hbase/spark/datasources/JavaBytesEncoder$`
    - See: [HBASE-22769](https://issues.apache.org/jira/browse/HBASE-22769)  
    - Example of how to use SQL filter pushdown
  ``` 
  val df = spark.read.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.table", "testspark").option("hbase.spark.use.hbasecontext", false).option("hbase.spark.pushdown.columnfilter", true).load()
  df.filter("id<10").show()
  ```
  
### Apache HBase-Spark connector tunables
- There are several tunable in the Apache Hbase-Spark connector, for example:
  - `hbase.spark.query.batchsize` - Set the maximum number of values to return for each call to next() in scan.
  - `hbase.spark.query.cachedrows` - The number of rows for caching that will be passed to scan.
  - Details of the [available configuration at this link](https://github.com/apache/hbase-connectors/blob/master/spark/hbase-spark/src/main/scala/org/apache/hadoop/hbase/spark/datasources/HBaseSparkConf.scala)  

---
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

- Read the HBase table from Spark
  ``` 
  val df = spark.read.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.table", "testspark").option("hbase.spark.use.hbasecontext", false).load()
  df.show()
  ```

- Read back from Spark using a filter, without server-side installation for SQL filter pushdown [HBASE-22769](https://issues.apache.org/jira/browse/HBASE-22769)
  ``` 
  val df = spark.read.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.table", "testspark").option("hbase.spark.use.hbasecontext", false).option("hbase.spark.pushdown.columnfilter", false).load()
  df.show()
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
with the important change when running Spark of substituting spark-shell with pyspark.
See also above for "Configuration and setup" how to configure Hbase client and server.
  
- Write to HBase with Spark
  ```  
  df = spark.sql("select id, 'myline_'||id  name from range(10)")
  df.write.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.namespace", "default").option("hbase.table", "testspark").option("hbase.spark.use.hbasecontext", False).save()
  ```

- Read from HBase with Spark

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
