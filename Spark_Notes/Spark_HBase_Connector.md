# Apache Spark-HBase Connector

- Spark needs a connector to access HBase
 - Which connector to use?
   - **[Apache Hbase Connectors](https://github.com/apache/hbase-connectors)** provides a Spark-Hbase connector
   - [Hortonworks Spark-HBase connector](https://github.com/hortonworks-spark/shc) has been quite popular
    over the years, it appears to be no more supported nor updated.

- How to use the Apache Spark Hbase connector?
  - **Spark 2.x:** Deploy the packages from maven (or compile from source). Example:
  ```
  bin/spark-shell --master yarn --num-executors 2 --executor-cores 2 \
    --packages org.apache.hbase:hbase-server:2.2.6,org.apache.hbase:hbase-common:2.2.6,org.apache.hbase:hbase-zookeeper:2.2.6, \
      org.apache.hbase.connectors.spark:hbase-spark:1.0.0,org.scala-lang:scala-library:2.11.12 \
    --conf spark.security.credentials.hbase.enabled=true
  ```
  
- **Spark 3.x:** How to use the Spark-HBase connector ?
  - You need to compile the connector with scala 2.12 (Spark 3.x does not support scala 2.11)
  - As of October 2020, you need an extra small set of changes to be able to build and use with Spark 3.0
    - See the [HBase-connectors repo experimental branch for Spark 3](https://github.com/LucaCanali/hbase-connectors/tree/spark3/spark) 
  - Build with (example):
    ```
    mvn -Dspark.version=3.0.1 -Dscala.version=2.12.10 -Dscala.binary.version=2.12 -Dhbase.version=2.2.6 -Dhadoop.profile=3.0 -Dhadoop-three.version=3.2.1 -DskipTests clean package
    ```
  - Deploy with:
  ```
  bin/spark-shell --master yarn --num-executors 2 --executor-cores 2 \
  --jars <path>/hbase-spark-1.0.1-SNAPSHOT.jar \
  --packages org.apache.hbase:hbase-server:2.2.6,org.apache.hbase:hbase-common:2.2.6,org.apache.hbase:hbase-mapreduce:2.2.6, \
    org.apache.hbase:hbase-zookeeper:2.2.6,org.scala-lang:scala-library:2.12.10 \
  --conf spark.security.credentials.hbase.enabled=true
  ```

- Important notes:
  - You need the hbase client configuration file `hbase-site.xml` 
    - Copy it to `SPARK_CONF_DIR` (default is $SPARK_HOME/conf`, note: HBASE_CONF_DIR does not work)
    - Note: possibly you need to send the file to the executors via `--files hbase-site.xml` (note this is not needed in my environment)

  - On HBase:
    `grant '<your_username_here>', 'X', 'hbase:meta'`

---
## How to run a test workload of Spark writing and reading from HBase using the Spark-Habse connector:

    
### Write + Read, example 1


- On HBase, create the test table and grant the related privileges to your user:
  ```
  create 'testspark1', 'cf'
  grant '<your_username_here>', 'XRW', 'testspark1'
  ```

- On Spark:
  - Start spark 2.x or 3.x as detailed above
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

### Another option for writing and reading by explicitly specifing the catalog in JSON format
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
    |"table":{"namespace":"default", "name":"testspark2"},
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
    |"table":{"namespace":"default", "name":"testspark2"},
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
    --packages org.apache.hbase:hbase-server:2.2.6,org.apache.hbase:hbase-common:2.2.6,org.apache.hbase:hbase-zookeeper:2.2.6, \
      org.apache.hbase.connectors.spark:hbase-spark:1.0.0,org.scala-lang:scala-library:2.11.12 \
    --conf spark.security.credentials.hbase.enabled=true
  ```

  - Spark 3.x
  ```
  bin/pyspark --master yarn --num-executors 2 --executor-cores 2 \
  --jars <path>/hbase-spark-1.0.1-SNAPSHOT.jar \
  --packages org.apache.hbase:hbase-server:2.2.6,org.apache.hbase:hbase-common:2.2.6,org.apache.hbase:hbase-mapreduce:2.2.6, \
    org.apache.hbase:hbase-zookeeper:2.2.6,org.scala-lang:scala-library:2.12.10 \
  --conf spark.security.credentials.hbase.enabled=true
  ```
  
  - Important notes:
    - You need the hbase client configuration file `hbase-site.xml` 
      - Copy it to `SPARK_CONF_DIR` (default is $SPARK_HOME/conf`, note: HBASE_CONF_DIR does not work)
      - Note: possibly you need to send the file to the executors via `--files hbase-site.xml` (note this is not needed in my environment)
  
    - On HBase:
      `grant '<your_username_here>', 'X', 'hbase:meta'`
      
- Write
  ```  
  df = spark.sql("select id, 'myline_'||id  name from range(10)")

  df.write.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.namespace", "default").option("hbase.table", "testspark1").option("hbase.spark.use.hbasecontext", False).save()
  ```

- Read back from Spark

  ```
  df = spark.read.format("org.apache.hadoop.hbase.spark").option("hbase.columns.mapping","id INT :key, name STRING cf:name").option("hbase.table", "testspark1").option("hbase.spark.use.hbasecontext", False).load()

  df.show()
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
  df = spark.read.options(catalog=catalog).format("org.apache.hadoop.hbase.spark").option("hbase.spark.use.hbasecontext", false).load()
  
  df.show()
  ```
