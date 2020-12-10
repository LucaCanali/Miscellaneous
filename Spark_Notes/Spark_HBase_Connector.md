# Apache Spark-HBase Connector

### Why
Spark needs a connector library to access HBase.
  - **[Apache HBase Connectors](https://github.com/apache/hbase-connectors)** provides a Spark-HBase connector
   - [Hortonworks Spark-HBase connector](https://github.com/hortonworks-spark/shc) is another connector, it has been quite popular
    over the years, it appears to be no more supported nor updated.

### Configuration
  - You need the HBase client configuration file `hbase-site.xml` 
    - Copy it to `SPARK_CONF_DIR` (default is $SPARK_HOME/conf`, note: HBASE_CONF_DIR does not work)
  - See also the note below on server-side jar configuration to use SQL filter pushdown

### Spark 2.x and the Apache Spark HBase connector 
  - Deploy the connector using packages from Maven Central. Example:
  ```
  bin/spark-shell --master yarn --num-executors 1 --executor-cores 2 \
    --packages org.apache.hbase:hbase-server:2.2.4,org.apache.hbase:hbase-common:2.2.4,org.apache.hbase:hbase-zookeeper:2.2.4,org.apache.hbase.connectors.spark:hbase-spark:1.0.0
  ```
  
### Spark 3.x and the Apache Spark HBase connector
- You need to compile the connector with scala 2.12 (Spark 3.x does not support scala 2.11)
- An extra PR is needed: 
  - See HBase Connectors - [HBASE-25326](https://issues.apache.org/jira/browse/HBASE-25326)
  - See also HBase-connectors fork and experimental [branch for Spark 3 compatibility](https://github.com/LucaCanali/hbase-connectors/tree/compileWithSpark3) 

 - Build as in this example (customize HBase, Spark and Hadoop versions, as needed):  
    ```
    mvn -Dspark.version=3.0.1 -Dscala.version=2.12.10 -Dscala.binary.version=2.12 -Dhbase.version=2.2.4 -Dhadoop.profile=3.0 -Dhadoop-three.version=3.2.0 -Dhadoop.version=3.2.0 -DskipTests clean package
    ```
  - Deploy using Spark 3.0, as in this example:
  ```
  # Customize the JAR path, for convenience there are versions uploaded to a web server
  JAR1=http://cern.ch/canali/res/hbase-spark-1.0.1_spark-3.0.1-cern1_4.jar
  JAR2=http://cern.ch/canali/res/hbase-spark-protocol-shaded-1.0.1_spark-3.0.1-cern1_4.jar
  bin/spark-shell --master yarn --num-executors 1 --executor-cores 2 \
  --jars $JAR1,$JAR2 --packages org.apache.hbase:hbase-shaded-mapreduce:2.2.4
  ```

  - Other options:
    - Deploy from maven central using a fork with fixes to run on Spark 3
      - Note this is a workaround solution, as I had to rename the group id to ch.cern to push to maven central
      - `bin/spark-shell --master yarn --num-executors 1 --executor-memory 8g --packages ch.cern.hbase.connectors.spark:hbase-spark:1.0.1_spark-3.0.1_4`
    - **CERN users only**: deploy from artifactory.cern.ch (only visible from CERN network)
      - `bin/spark-shell --master yarn --num-executors 1 --executor-memory 8g --repositories https://artifactory.cern.ch/beco-thirdparty-local --packages org.apache.hbase.connectors.spark:hbase-spark:1.0.1_spark-3.0.1-cern1_4`

---
## How to run a test workload of Spark writing and reading from HBase using the Spark-Hbase connector:

### Spark-HBase connector: write and read example 


- On HBase, create the test table and grant the related privileges to your user (use `hbase shell`):
  ```
  create 'testspark1', 'cf'
  grant '<your_username_here>', 'XRW', 'testspark1'
  ```
  - Note this may be too needed: `grant '<your_username_here>', 'X', 'hbase:meta'`
 
- On Spark:
  - Start Spark 2.x or 3.x as detailed above
  - Write:
  ```  
  val df = sql("select id, 'myline_'||id  name from range(10)")
  df.write.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.namespace", "default").option("hbase.table", "testspark1").option("hbase.spark.use.hbasecontext", false).save()
  ```
  
- Read back from Spark
  ``` 
  val df = spark.read.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.table", "testspark1").option("hbase.spark.use.hbasecontext", false).load()
  df.show()
  ```

- Read back from Spark using a filter, without server-side installation for SQL filter pushdown [HBASE-22769](https://issues.apache.org/jira/browse/HBASE-22769)
  ``` 
  val df = spark.read.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.table", "testspark1").option("hbase.spark.use.hbasecontext", false).option("hbase.spark.pushdown.columnfilter", false).load()
  df.show()
  ```

### SQL Filter pushdown and server-side jar configuration

- This allows to push down filter predicates to HBase
  - It is configured with `.option("hbase.spark.pushdown.columnfilter", true)` which is the default. 
  - This requires additional configuration on the HBase server side, in particular one needs to have
    a few jars in the HBase region servers CLASSPATH: scala-library, hbase-spark and hbase-spark-protocol-shaded.
    For example for Spark 2.4:
    ```
    scala-library-2.11.12.jar
    hbase-spark-1.0.0.jar
    hbase-spark-protocol-shaded-1.0.0.jar
    ```
    For example for Spark 3.0:
    ```
    scala-library-2.12.10.jar
    hbase-spark-1.0.1_spark-3.0.1-cern1_3.jar
    hbase-spark-protocol-shaded-1.0.1_spark-3.0.1-cern1_3.jar
    ```
  - If this is not set you will get
  an error: `java.lang.NoClassDefFoundError: org/apache/hadoop/hbase/spark/datasources/JavaBytesEncoder$`
    - See: [HBASE-22769](https://issues.apache.org/jira/browse/HBASE-22769)  
    - Example of how to use SQL filter pushdown
  ``` 
  val df = spark.read.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.table", "testspark1").option("hbase.spark.use.hbasecontext", false).option("hbase.spark.pushdown.columnfilter", true).load()
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
  - Start spark 2.x or 3.x as detailed above

  - Write:  
  ```
  import org.apache.hadoop.hbase.spark.datasources.HBaseTableCatalog

  val catalog = s"""{
    |"table":{"namespace":"default", "name":"testspark1"},
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

- Read back from Spark
  ```
  import org.apache.hadoop.hbase.spark.datasources.HBaseTableCatalog

  val catalog = s"""{
    |"table":{"namespace":"default", "name":"testspark1"},
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

- Note: this is almost the same as with Scala examples above, with the usual changes between spark-shell and pyspark

  - Spark 2.x
  ```
  bin/pyspark --master yarn --num-executors 2 --executor-cores 2 \
   --packages org.apache.hbase:hbase-server:2.2.4,org.apache.hbase:hbase-common:2.2.4,org.apache.hbase:hbase-zookeeper:2.2.4,org.apache.hbase.connectors.spark:hbase-spark:1.0.0
  ```

  - Spark 3.x (see details above in "Spark 3.x and the Apache Spark Hbase connector")
  ```
  bin/pyspark --master yarn --num-executors 2 --executor-cores 2 \
   --jars $JAR1,$JAR2 \
   --packages org.apache.hbase:hbase-server:2.2.4,org.apache.hbase:hbase-common:2.2.4,org.apache.hbase:hbase-mapreduce:2.2.4,org.apache.hbase:hbase-zookeeper:2.2.4,org.scala-lang:scala-library:2.12.10
  ```
  
  - Important notes:
    - You need the HBase client configuration file `hbase-site.xml` 
      - Copy it to `SPARK_CONF_DIR` (default is $SPARK_HOME/conf`, note: HBASE_CONF_DIR does not work)
      
- Write
  ```  
  df = spark.sql("select id, 'myline_'||id  name from range(10)")
  df.write.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.namespace", "default").option("hbase.table", "testspark1").option("hbase.spark.use.hbasecontext", False).save()
  ```

- Read back from Spark

  ```
  df = spark.read.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.table", "testspark1").option("hbase.spark.use.hbasecontext", False).load()
  df.show()
  df.filter("id==9").show() # see above note on SQL filter pushdown server-side configuration
  ```
  
- Another option for reading: explicitly specify the catalog in JSON format:
  ```
  import json

  catalog = json.dumps(
    {
        "table":{"namespace":"default", "name":"test"},
        "rowkey":"key",
        "columns":{
            "id":{"col":"key", "type":"int"},
            "name":{"cf":"cf", "col":"name", "type":"string"}
        }
    })

  # Note: this throws errors, needs to be understood
  df = spark.read.options(catalog=catalog).format("org.apache.hadoop.hbase.spark").option("hbase.spark.use.hbasecontext", False).load()
  
  df.show()
  ```
