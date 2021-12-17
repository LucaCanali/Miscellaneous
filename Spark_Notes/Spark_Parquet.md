# Spark and Parquet

Apache Parquet is one of the preferred data formats when using Apache Spark.  
Basic use of the DataFrame reader and writer with Parquet:
```
val df = spark.read.parquet("file path") // read
df.write.mode("overwrite").parquet("file path") // write
```
[Link to the Spark docs](https://spark.apache.org/docs/latest/sql-data-sources-parquet.html)

## Configuration options
There are several configurable parameters for the Parquet datasources, see:
[link with a list of Apache Parquet parameters](https://github.com/apache/parquet-mr/blob/master/parquet-hadoop/README.md`)

A few notable options:
```
.option("compression", compression_type)    // compression algorithm, default is snappy, use none for no compression
.option("parquet.block.size",128*1024*1024) // Parquet rowgroup size, default 128 MB 
```


## Parquet 1.12 new features and Spark 3.2

Spark 3.2 comes with Parquet v1.12 (previous releases, Spark 3.1 and 2.4 use Parquet Spark 1.10)
Notable Parquet features newly available in Spark 3.2 are:

- Column indexes
  - desc and link to doc
- Bloom filters
    - desc and link to doc
- Encryption
   - desc and link to doc

**Parquet version:**
You need to write files with the Parquet version 1.12 or higher to use the features listed above.
With Spark this means using Spark 3.2.0, or higher when available.

## How to check the Parquet version :
As Parquet format evolves, more metadata is made available which is used by new features.
The Parquet version used to write a given file is stored in the metadata.
How to extract metadata information:

- **parquet-cli**
  - example: `hadoop jar parquet-cli/target/parquet-cli-1.12.2-runtime.jar org.apache.parquet.cli.Main meta <path>/myParquetFile`
  - see also [Tools for Parquet Diagnostics](../Tools_Parquet_Diagnostics.md)

- **Hadoop API** ...
  - example of using Hadoop API from the spark-shell CLI
  ```
  // customize with the file path and name
  val fullPathUri = java.net.URI.create("<path>/myParquetFile")
   
  // crate a Hadoop input file and opens it with ParquetFileReader
  val in = org.apache.parquet.hadoop.util.HadoopInputFile.fromPath(new org.apache.hadoop.fs.Path(fullPathUri), spark.sessionState.newHadoopConf())
  val pf = org.apache.parquet.hadoop.ParquetFileReader.open(in)

  // Get the Parquet file version
  pf.getFooter.getFileMetaData.getCreatedBy
  
  // Info on file metadata
  print(pf.getFileMetaData)
  print(pf.getRowGroups)
  ```

## Convert Parquet files to a newer version by copying them using Spark
 - Use a recent Spark to read the source Parquet files and save them with the Parquet version
  used by Spark. For example with Spark 3.2.0 you can write files in Parquet version 1.12.1
 - Example of how to copy Parquet files for the TPCDS benchmark
```
bin/spark-shell --master yarn --driver-memory 4g --executor-memory 50g --executor-cores 10 --num-executors 20 --conf spark.sql.shuffle.partitions=400

val inpath="/project/spark/TPCDS/tpcds_1500_parquet_1.10.1/"
val outpath="/user/canali/TPCDS/tpcds_1500_parquet_1.12.1/"
val compression_type="snappy"
// val compression_type="zstd"

// copy partitioned tables of the TPCDS benchmark
// compact each directory into 1 file with repartition
val tables_partition=List(("catalog_returns","cr_returned_date_sk"), ("catalog_sales","cs_sold_date_sk"), ("inventory","inv_date_sk"), ("store_returns","sr_returned_date_sk"), ("store_sales","ss_sold_date_sk"), ("web_returns","wr_returned_date_sk"), ("web_sales","ws_sold_date_sk"))
for (t <- tables_partition) {
  println(s"Copying partitioned table $t")
  spark.read.parquet(inpath + t._1).repartition(col(t._2)).write.partitionBy(t._2).mode("overwrite").option("compression", compression_type).parquet(outpath + t._1)
}

// copy non-partitioned tables of the TPCDS benchmark
// compact each directory into 1 file with repartition
val tables_nopartition=List("call_center","catalog_page","customer","customer_address","customer_demographics","date_dim","household_demographics","income_band","item","promotion","reason","ship_mode","store","time_dim","warehouse","web_page","web_site")
for (t <- tables_nopartition) {
  println(s"Copying table $t")
  spark.read.parquet(inpath + t).coalesce(1).write.mode("overwrite").option("compression", compression_type).parquet(outpath + t)
}
```

## Column indexes
What are they good for
Example
