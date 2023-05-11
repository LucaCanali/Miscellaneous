# Apache Spark and Parquet
Notes on configuration, features, and diagnostics when using the Parquet data format with Spark.  
Links to content:    

- [Intro and basics](#basic-use-of-the-dataframe-reader-and-writer-with-parquet)
- [Configurations and options when using Parquet with Spark](#parquet-configuration-options) 
- Parquet files and their version
  - [version discovery](#parquet-version-discovery)
  - [version update with file overwrite](#parquet-version-update)
- See also [Parquet Diagnostics Tools](Tools_Parquet_Diagnostics.md)
  - it covers parquet-cli, PyArrow Parquet metadata reader, parquet_tools, and parquet_reader
- Parquet new features in Spark 3.2 and 3.3
  - [Note on Parquet 1.12 new features](#parquet-112-new-features-and-spark-32)
  - [Filter pushdown improvement with column indexes](#spark-filter-push-down-and-parquet-column-indexes)
  - [Diagnostics: Column and offset indexes](#column-and-offset-indexes)
  - [Bloom filters, configuration, use, and diagnostics](#bloom-filters-in-parquet)
  - [Vectorized Parquet reader for complex datatypes](#vectorized-parquet-reader-for-complex-datatypes)
  - [Hidden metadata columns for Parquet reader](#spark-hidden-metadata-columns-for-parquet-reader)
  - [Push down aggregates](#push-down-aggregates)
  - [Enable matching schema columns by field id](#enable-matching-schema-columns-by-field-id)
  

### Basic use of the Apache Spark DataFrame reader and writer with Parquet:

Data formats make for an important part of data platforms.
Apache Parquet is one of the preferred data file formats when using Apache Spark for data analysis.
Apache ORC is another data file format that shares many of the characteristics of Parquet,
see also [Parquet-ORC note](Spark_ORC_vs_Parquet.md)  
Some key features of Parquet are:
  - it is a columnar format
  - allows compression and encoding 
  - Spark has several optimizations that considerably improve performance when dealing with Parquet, including
    - a vectorized reader for Parquet, which
    - support for filter pushdown 
    - support for partitioning and large files
      - Spark can create multiple partitions out large files to improve parallelism
      - partition discovery allows reading partitioned tables from their schema layout into nested folders  
    - schema evolution


### Notes on the use of Parquet writer

A quick recap of the basics when using Parquet with Spark.  
For more details see [Spark datasource documentation](https://spark.apache.org/docs/latest/sql-data-sources-parquet.html)
```
val df = spark.read.parquet("file path") // read
df.write.mode("overwrite").parquet("file path") // write
```

- Example: write using Spark and compact the output to only 1 output file.  
This is how you can write a Spark DataFrame and compact the result to 1 file.  
Note this will limit performance (number of concurrent tasks), so use with caution, typically only for small files  
`df.coalesce(1).write.mode("overwrite").parquet("mypath_path/myfile.parquet")`  
  

- Example options you can use when writing a DataFrame
```
df.coalesce(N_partitions). // use coalesce or repartition to reduce/increase the number of partitions in the df, 
   sortWithinPartitions(col("optinalSortColumn")).
   write.    
   partitionBy(col("colPartition1"), col("colOptionalSubPart")). // optional partitioning column(s)
   bucketBy(numBuckets, "colBucket").  // bucketBy can be used with partitionBy only with saveAsTable, see SPARK-19256
   format("parquet").
   mode("overwrite").                   //  Accepted save modes are 'overwrite', 'append', 'ignore', 'error', 'errorifexists', 'default'
   save("filePathandName")             // you can use saveAsTable as an alternative
```
  
- Example of how to write only 1 file per partition
Parquet table repartition is an operation that you may want to use in the case you ended up with
multiple small files into each partition folder and want to compact them in a smaller number of larger files.
Example:
```
val df = spark.read.parquet("myPartitionedTableToCompact")

df.repartition(col("colPartition1"),col("colOptionalSubPartition"))
  .write.partitionBy("colPartition1","colOptionalSubPartition")
  .parquet("filePathandName")
```
   
- Example of how to write partitioned data sorted by partition  
Data sorting can improve encoding and compression performance, it can also be useful for performance
at query time
```
# write the dataframe to Parquet
# apply repartitioning and sort before writing
from pyspark.sql.functions import col
(df.
   repartition(num_partitions, col("repartition_column")).
   sortWithinPartitions(col("repartition_column"), col("additional_orderby_column")).
   write.
   mode("overwrite").
   partitionBy("repartition_column")  // optional, if you use this, each partition will be in a deparate folder
   format(data_format).
   option("compression", compression_type).
   save(f"{path}/table_name")
)
```
  
### Parquet configuration options
There are many configurable parameters for the Parquet library and Spark data source, see an extensive list at:  
[link with a list of Apache Parquet parameters](https://github.com/apache/parquet-mr/blob/master/parquet-hadoop/README.md)

Apache Parquet configuration parameters can be used withe in Spark in multiple ways:
- 1. as an option to the Spark DataFrame writer and/or reader, example: `.option("parquet.block.size", 128*1024*1024")`
- 2. as a Spark configuration parameter
  - example: `--conf spark.hadoop.parquet.block.size=128*1024*1024`
  - note the prefix `spark.hadoop` when you want to pass a Hadoop configuration via Spark configuration
  - Spark configuration options can also be set programmatically when creating the Spark Session
  - Spark configuration can also be stored in the configuration file `spark-defaults.conf`

In addition, the Spark DataFrame reader and writer have a limited number of options that can be used to configure the Parquet library,
see [Spark documentation](https://spark.apache.org/docs/latest/sql-data-sources-parquet.html#data-source-option) for details.

There are also specific configurations for the Spark DataFrame reader and Writer that apply to reading/writing Parquet too.  
Some relevant Spark configurations for providing support for large files:  
- Read: `spark.conf.set("spark.sql.files.maxPartitionBytes", ..)` (default 128 MB) can be used to create multiple partitions out large files with multiple rowgroups
- Write: `spark.conf.set("spark.sql.files.maxRecordsPerFile", ...)` defaults to 0, use if you need to limit size of files being written
- `spark.sql.parquet.filterPushdown` (default true) enables/disables filter pushdown
- `spark.sql.parquet.enableNestedColumnVectorizedReader` (default true) enables/disables vectorized reader for nested Parquet columns

Example:  
- A few notable examples and options applicable to Apache Spark Parquet DataFrame writer:  
(note if you rather want to use these parameters at the SparkSession level, as Spark configuration (`--conf`) see the discussed above).  
```
.option("compression", compression_type)      // compression algorithm, default when using Spark is snappy, use none for no compression
.option("parquet.block.size", 128*1024*1024)  // Parquet rowgroup (block) size, default 128 MB
.option("parquet.page.size", 1024*1024)       // parquet page size, default 1 MB
.option("parquet.page.row.count.limit)        // the maximum number of rows per page, default 20000
.option("parquet.bloom.filter.enabled","true") // write bloomfilters, default is false
.option("parquet.bloom.filter.expected.ndv#column_name", num_values) // tuning for bloom filters
.option("parquet.enable.dictionary","true")   // enable/disable dictionary encoding, default is true 
```

- A few additional options for Apache Spark Parquet DataFrame reader:
```
.option("parquet.filter.bloom.enabled","true")       // use bloom filters (default: true)
.option("parquet.filter.columnindex.enabled","true") // use column indexes (default: true)
.option("parquet.filter.dictionary.enabled","true")  // use row group dictionary filtering (default: true)
.option("parquet.filter.stats.enabled", "true")      // use row row group stats filtering (default: true)
```

### Parquet version discovery

As the Parquet format continues to evolve, more metadata is being added to support new features.
The version of Parquet used to write a given file is stored in its metadata. 
If you are using Parquet files written with older versions of Spark and the corresponding old Parquet library versions,
you may not be able to use features introduced in recent versions, such as column indexes available in the Spark DataFrame
Parquet writer starting from version 3.2.0. When you upgrade Spark, you should also consider upgrading the metadata in
your Parquet files to take advantage of these new features (see an example of how to do that later in this note).

### How to check the Parquet version:

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

### Parquet version update

**How convert Parquet files to a newer version by copying them using Spark**
 - Use a recent Spark to read the source Parquet files and save them with the Parquet version
   used by Spark. For example by using Spark 3.3.1 you can write files in Parquet version 1.12.2
   This is a brute-force approach, however I am not aware of any other method to "upgrade" Parquet metadata.
 - Example of how to copy Parquet files for the TPCDS benchmark
```
bin/spark-shell --master yarn --driver-memory 4g --executor-memory 50g --executor-cores 10 --num-executors 20 --conf spark.sql.shuffle.partitions=400

val inpath="/project/spark/TPCDS/tpcds_1500_parquet_1.10.1/"
val outpath="/project/spark/TPCDS/tpcds_1500_parquet_1.12.2/"
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

### Parquet 1.12 new features and Spark 3.2
Spark 3.2 and 3.3 deploy Parquet v1.12.x (it's Parquet 1.12.2 with Spark 3.3.1) with a few notable new features over previous releases.  

- Column indexes
  - column indexes help optimizing the execution of filter predicates under certain circumstances (read further for details)
  - column indexes are **on** by default.
- Bloom filters
  - bloom filters are also intended to improve execution for certain types of filters
  - bloom filters are **off** by default 
- Encryption
  - see https://spark.apache.org/docs/latest/sql-data-sources-parquet.html#columnar-encryption 

## Spark filter push down and Parquet column indexes

When scanning Parquet files with Spark using a filter (for example a "where" condition in Spark SQL)
Spark will try to optimize the physical plan by pushing down the filter to Parquet.
The techniques available with Parquet files are:
- Partition pruning if your (set of) files is partitioned, and your filter is on the partitioning column.
  - typically this means that your table is stored on the storage system (HDFS, S3, etc) on a nested folder 
  structure with folder names like <partition_column_name=value>
- Predicate push down at the Parquet row group level. 
  - This will use statistics (min and max value) stored for each column with row group granularity 
  (the default row group size is 128 MB)
  - Column chunk dictionaries may be available with dictionary encoding   
- Additional structures introduced in Parquet 1.11 and available when using Spark 3.2.0 and higher are column and offset indexes
  - these structures store statistics (including min and max values) at the granularity of the Parquet page.
  They make possible predicate push down at the page level, which has a default size is 1 MB,
  that is a much finer granularity than the row group size.
- Note: the use of column statistics, both at row group and page level (column index), 
  is typically much more effective when data is stored sorted in the Parquet files, this limits the range of values
  in a given page or row group, as opposed to have to deal with a set of values that span across the full range in the table.
- Bloom filters are another structure introduced in recent versions of Parquet that can be used to improve the execution of filter predicates,
  more on this later in this document

## Example: Spark using Parquet column indexes

Test dataset and preparation:  
- The Parquet test file used below `parquet112file_sorted` is extracted from the TPCDS benchmark table
  [web_sales](https://github.com/apache/spark/blob/master/sql/core/src/test/scala/org/apache/spark/sql/TPCDSSchema.scala#L162)
- the table (parquet file) contains data sorted on the column ws_sold_time_sk
- it's important that the data is sorted, this groups together values in the filter column "ws_sold_time_sk", if the values
  are scattered the column index min-max statistics will have a wide range and will not be able to help with skipping data 
- the sorted dataset has been created using
  `spark.read.parquet("path + "web_sales_piece.parquet").sort("ws_sold_time_sk").coalesce(1).write.parquet(path + "web_sales_piece_sorted_ws_sold_time_sk.parquet")`
- Download the test data:
  - [web_sales_piece.parquet](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Parquet_Tests/web_sales_piece.parquet)   
  - [web_sales_piece_sorted_ws_sold_time_sk.parquet](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Parquet_Tests/web_sales_piece_sorted_ws_sold_time_sk.parquet)

Tests:
1. **Fast** (reads only 20k rows): Spark reading with a filter that makes use of column and offset indexes:
```
val path = "/home/luca/test/web_sales_sample_parquet1.12.2/"
val df = spark.read.parquet(path + "web_sales_piece_sorted_ws_sold_time_sk.parquet")

val q1 = df.filter("ws_sold_time_sk=28801")
val plan = q1.queryExecution.executedPlan
q1.collect
// Use Spark metrics to see how many rows were processed
// This is also avilable for the WebUI in graphical form
val metrics = plan.collectLeaves().head.metrics
metrics("numOutputRows").value

res: Long = 20000
```
The result is that only 20000 rows were processed, this corresponds to processing just a few pages,
and it is driven by the min-max value statistics in the column index for column ws_sold_time_sk.
The column index is crated by default in Spark version 3.2.x and higher.

2. **Slow** (reads 2M rows): Same as above but this time we disable the use of column indexes.
Note this is also what happens if you use Spark versions prior to Spark 3.2.0 (notably Spark 2.x) to read the file.
```
val path = "/home/luca/test/web_sales_sample_parquet1.12.2/"
// disable the use of column indexes for testing purposes
val df = spark.read.option("parquet.filter.columnindex.enabled","false").parquet(path + "web_sales_piece_sorted_ws_sold_time_sk.parquet")

val q1 = df.filter("ws_sold_time_sk=28801")
val plan = q1.queryExecution.executedPlan
q1.collect
// Use Spark metrics to see how many rows were processed
val metrics = plan.collectLeaves().head.metrics
metrics("numOutputRows").value

res: Long = 2088626
```
The result is that all the rows in the row group (2088626 rows in the example) were read as Spark 
could not push the filter down to the Parquet page level.

### Diagnostics and internals of Column and Offset Indexes

Column indexes are structures that can improve filters performance when reading Parquet files.  
Column indexes are "on by default".
Column indexes provide stats (min and max values) on the data at the page granularity, which can be used to evaluate filters. Similar statistics are available
at rowgroup level, however a rowgroup is typically 128MB in size, while pages are typically 1MB.  
Note: both row group and page sizes are configurable, see [Parquet configuration options]((#parquet-configuration-options)).    
Column indexes and their sibling, offset indexes, are stored in the footer of Parquet files version 1.11 and above.  
This has the additional advantage that when scanning Parquet files without applying filters, the footers with the column index data can simply be skipped.  
See a detailed [description of column and offset indexes in Parquet at this link](https://github.com/apache/parquet-format/blob/master/PageIndex.md)

### Tools to drill down on column index metadata in Parquet files**

- **parquet-cli**
  - example: `hadoop jar target/parquet-cli-1.12.2-runtime.jar org.apache.parquet.cli.Main column-index -c ws_sold_time_sk <path>/parquet112file`
  - see also [Tools for Parquet Diagnostics](../Tools_Parquet_Diagnostics.md)

- Example with the **Java API** from Spark-shell
   ```
   // customize with the file path and name
   val fullPathUri = java.net.URI.create("<path>/myParquetFile")

   // crate a Hadoop input file and opens it with ParquetFileReader
   val in = org.apache.parquet.hadoop.util.HadoopInputFile.fromPath(new org.apache.hadoop.fs.Path(fullPathUri), spark.sessionState.newHadoopConf())
   val pf = org.apache.parquet.hadoop.ParquetFileReader.open(in)

   // Get the Parquet file version
   pf.getFooter.getFileMetaData.getCreatedBy

   // columns index
   val columnIndex = pf.readColumnIndex(columns.get(0))
   columnIndex.toString.foreach(print)

   // offset index
   pf.readOffsetIndex(columns.get(0))
   print(pf.readOffsetIndex(columns.get(0)))
   ```
The output on a column that is sorted looks like:
```
row-group 0:
column index for column ws_sold_time_sk:
Boudary order: ASCENDING
                      null count  min                                       max
page-0                        45  29                                        12320
page-1                         0  12320                                     19782
page-2                         0  19782                                     26385
page-3                         0  26385                                     31758
page-4                         0  31758                                     36234
page-5                         0  36234                                     40492
page-6                         0  40492                                     44417
page-7                         0  44417                                     47596
page-8                         0  47596                                     52972
page-9                         0  52972                                     58388
page-10                        0  58388                                     62482
page-11                        0  62482                                     65804
page-12                        0  65804                                     68647
page-13                        0  68647                                     71299
page-14                        0  71303                                     74231
page-15                        0  74231                                     77978
page-16                        0  77978                                     85712
page-17                        0  85712                                     86399

offset index for column ws_sold_time_sk:
                          offset   compressed size       first row index
page-0                     94906              4759                     0
page-1                     99665              4601                 20000
page-2                    104266              4549                 40000
page-3                    108815              4415                 60000
page-4                    113230              4343                 80000
page-5                    117573              4345                100000
page-6                    121918              4205                120000
page-7                    126123              3968                140000
page-8                    130091              4316                160000
page-9                    134407              4370                180000
page-10                   138777              4175                200000
page-11                   142952              4012                220000
page-12                   146964              3878                240000
page-13                   150842              3759                260000
page-14                   154601              3888                280000
page-15                   158489              4048                300000
page-16                   162537              4444                320000
page-17                   166981               200                340000
```

### Bloom filters in Parquet
Parquet 1.12 introduces the option of generating and storing bloom filters in Parquet metadata on the file footer.
Bloom filters improve the performance of certain filter predicates.
They are particularly useful with 
 - high cardinality columns to overcome the limitations of using Parquet dictionaries.
 - for filters that seek for values that are likely not in the table/DataFrame, this is because in Bloom filters
   false positive matches are possible, but false negatives are not.
You can find the details on [bloom filters in Apache Parquet at this link](https://github.com/apache/parquet-format/blob/master/BloomFilter.md)

**Configuration**

Important configurations for writing bloom filters in Parquet files are:
```
.option("parquet.bloom.filter.enabled","true") // write bloom filters for all columns, default is false
.option("parquet.bloom.filter.enabled#column_name", "true") // write bloom filter for the given column
.option("parquet.bloom.filter.expected.ndv#column_name", num_values) // tuning for bloom filters, ndv = number of distinct values
.option("parquet.bloom.filter.max.bytes", 1024*1024) // The maximum number of bytes for a bloom filter bitset, default 1 MB
```

This is an example of how to read a Parquet file without bloom filter (for example because created with 
an older version of Spark/Parquet) and add the bloom filter, with additional tuning of the bloom filter parameters for one of the columns:
```
val df = spark.read.parquet("<path>/web_sales")
df.coalesce(1).write.option("parquet.bloom.filter.enabled","true").option("parquet.bloom.filter.expected.ndv#ws_sold_time_sk", 25000).parquet("<myfilepath")
```

**Bloom filter example**
This how you can check the I/O performed when reading Parquet, it allows to compare
the difference when using bloom filters vs. not using them.

Example:
```
// 1. prepare the test table

bin/spark-shell
val numDistinctVals=1e6.toInt
val df=sql(s"select id, int(random()*100*$numDistinctVals) randomval from range($numDistinctVals)")

df.coalesce(1).write.mode("overwrite").option("parquet.bloom.filter.enabled","true").option("parquet.bloom.filter.enabled#randomval", "true").option("parquet.bloom.filter.expected.ndv#randomval", numDistinctVals).parquet("/home/luca/test/testParquetFile/spark320_test_bloomfilter")
df.coalesce(1).write.mode("overwrite").option("parquet.bloom.filter.enabled","false").parquet("/home/luca/test/testParquetFile/spark320_test_bloomfilter_nofilter")

// note compare the size of the files with bloom filter and without
// in my test: it was 10107281 with bloom filter and 8010083 without

:quit

// 2. read tests:

// 2a. with bloom filter
bin/spark-shell

val df =spark.read.option("parquet.filter.bloom.enabled","true").parquet("/home/luca/test/testParquetFile/spark320_test_bloomfilter")
val q1 = df.filter("randomval=1000000") // filter for a value that is not in the file
q1.collect

// print I/O metrics
org.apache.hadoop.fs.FileSystem.printStatistics()

// Output
FileSystem org.apache.hadoop.fs.RawLocalFileSystem: 1095643 bytes read

:quit

// 2b. without bloom filter
bin/spark-shell

val df =spark.read.option("parquet.filter.bloom.enabled","false").parquet("/home/luca/test/testParquetFile/spark320_test_bloomfilter")
val q1 = df.filter("randomval=1000000") // filter for a value that is not in the file
q1.collect

// print I/O metrics

// Output
FileSystem org.apache.hadoop.fs.RawLocalFileSystem: 8303682 bytes read
```

For demo purposes this example disables the use of dictionary and column index filters,
which is an optimization that improves filter execution too`.option("parquet.filter.dictionary.enabled","false")`
```
bin/spark-shell

// val df =spark.read.option("parquet.filter.bloom.enabled","false").option("parquet.filter.dictionary.enabled","true").option("parquet.filter.columnindex.enabled","false").option("parquet.filter.dictionary.enabled","false").option("parquet.filter.columnindex.enabled","false").parquet("<myParquetfile_withbloomfilter>")
val df =spark.read.option("parquet.filter.bloom.enabled","true").option("parquet.filter.dictionary.enabled","true").option("parquet.filter.columnindex.enabled","false").option("parquet.filter.dictionary.enabled","false").option("parquet.filter.columnindex.enabled","false").parquet("<myParquetfile_withbloomfilter>")
val q1 = df.filter("ws_sold_time_sk=50000")
q1.collect

// measure I/O with and without bloom filter
org.apache.hadoop.fs.FileSystem.printStatistics()

Results:
without optimized filters (full row group scan): 23532456 bytes read,
with bloom filter: 283560 bytes read,
```

**How to read Parquet bloom filter metadata**

This is how you can read metadata about the bloom filter in Apache Parquet using 
the Java API for spark-shell
```
val fullPathUri = java.net.URI.create("<my_file_path>")

val in = org.apache.parquet.hadoop.util.HadoopInputFile.fromPath(new org.apache.hadoop.fs.Path(fullPathUri), spark.sessionState.newHadoopConf())
val pf = org.apache.parquet.hadoop.ParquetFileReader.open(in)

val blocks = pf.getFooter.getBlocks
val columns = blocks.get(0).getColumns

val bloomFilter=pf.readBloomFilter(columns.get(0))
```

### Vectorized Parquet reader for complex datatypes 
Feature added in Spark 3.3.0
Default is false, when true, Spark 3.3.0 extends the vectorized Parquet reader for complex datatypes.
In Spark 3.3.x this requires configuration (see below), as it is off (false) by default 
In (future) Spark 3.4.0 the configuration will be on by default.
Configuration:
`--conf spark.sql.parquet.enableNestedColumnVectorizedReader=true`

The performance gain can be high, in the examples with 
[Physics array data at this link](../Spark_Physics#1-dimuon-mass-spectrum-analysis)
the execution time goes from about 30 seconds to 10 seconds when using the vectorized reader.

### Spark hidden metadata columns for Parquet reader

Feature added in Spark 3.3.0
```
val df=spark.read.parquet("/tmp/testparquet1")

df.select("_metadata.file_path", "_metadata.file_name","_metadata.file_size", "_metadata.file_modification_time").show(2,false)
```

### Push down aggregates
Feature added in Spark 3.3.0
Default is false, when true, aggregates will be pushed down to Parquet for optimization
`--conf spark.sql.parquet.aggregatePushdown=true`

### Enable matching schema columns by field id

Feature added in Spark 3.3.0, see [SPARK-38094](https://issues.apache.org/jira/browse/SPARK-38094)
Default is false, when true, Parquet readers will first use the field ID to determine which Parquet columns to read.
It enables matching columns by field id for supported DWs like iceberg and Delta.
`--conf spark.sql.parquet.fieldId.read.enabled=true`
