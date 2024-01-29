# Get the best out of Apache Parquet using Apache Spark
This guide offers comprehensive insights into the configuration, features, and diagnostic tools 
relevant to using the Apache Parquet data format within Apache Spark.    

## Quick Navigation:
- [Introduction and Basics](#basic-use-of-apache-spark-dataframe-with-parquet)
  - [Guidelines for writing Parquet](#guidelines-for-parquet-writer-usage)  
- [Configurations and Options for Parquet in Spark](#parquet-configuration-options)
- Understanding Parquet File Versions
  - [Discovering and Checking the Parquet Files Version Used](#discovering-parquet-version)
  - [Updating Parquet Files Version via File Overwrite](#updating-parquet-file-versions)
- Parquet Diagnostics Tools 
  - [Parquet Diagnostics Tools note](Tools_Parquet_Diagnostics.md) In-depth look at tools like parquet-cli, PyArrow, parquet_tools, and more
- Selected improvements in Parquet usage for Spark 
  - [Exploring New Features in Parquet 1.12](#parquet-112-new-features-for-spark-32-and-higher)
  - [Enhanced Filter Pushdown with Column Indexes](#Spark_Parquet.md#spark-filter-push-down-and-parquet-column-indexes)
  - [Example of Spark using Parquet Column Indexes](#example-spark-using-parquet-column-indexes)
  - [Column and Offset Index Diagnostics](#diagnostics-and-internals-of-column-and-offset-indexes)
  - [Tools to Investigate Columns Index Metadata](#tools-to-drill-down-on-column-index-metadata-in-parquet-files)
  - [How to use Parquet Bloom Filters](#bloom-filters-in-parquet)
    - [Example of how to imrpove Spark jobs performance with Parquet bloom filters](#example-checking-io-performance-in-parquet-with-and-without-bloom-filters)
    - [How to read Parquet bloom filters metadata](#reading-parquet-bloom-filter-metadata-with-apache-parquet-java-api)
  - [Vectorized Reader for Complex Datatypes](#vectorized-parquet-reader-for-complex-datatypes)
  - [Accessing Hidden Metadata Columns](#spark-hidden-metadata-columns-for-parquet-reader)
  - [Aggregates Pushdown](#push-down-aggregates)
  - [Schema Column Matching by Field ID](#enable-matching-schema-columns-by-field-id)
  - [Lazy Materialization](#anticipating-lazy-materialization-enhancing-performance-in-spark)

### Key Advantages of Parquet in Spark

Apache Parquet is a columnar storage file format optimized for use with data processing frameworks 
like Apache Spark. It offers efficient data compression and encoding schemes.

- Columnar format enabling efficient data storage and retrieval
- Supports compression and encoding
- Optimizations in Spark for Parquet include:
  - Vectorized Parquet reader
  - Filter push down capabilities
  - Enhanced support for partitioning and handling large files

**ORC:** For a comparison of Apache Parquet with another popular data format, Apache ORC, refer to [Parquet-ORC Comparison](Spark_ORC_vs_Parquet.md).

### Basic Use of Apache Spark DataFrame with Parquet:

For a comprehensive understanding, refer to the 
[Spark datasource documentation](https://spark.apache.org/docs/latest/sql-data-sources-parquet.html).
To read and write dataframes using Parquet:

```scala
val df = spark.read.parquet("file path") // Read
df.write.mode("overwrite").parquet("file path") // Write
```

- Example: write using Spark and compact the output to just one single output file.  
This is how you can write a Spark DataFrame and compact the result to 1 file.  
Note this will limit performance (number of concurrent tasks), so use with caution, typically only for small files  
`df.coalesce(1).write.mode("overwrite").parquet("mypath_path/myfile.parquet")`  


### Guidelines for Parquet Writer Usage

- Example options you can use when writing a DataFrame
```
df.coalesce(N_partitions). // use coalesce or repartition to reduce/increase the number of partitions in the df, 
   sortWithinPartitions(col("my_optionalSortColumn")).
   write.    
   partitionBy(col("colPartition1"), col("colOptionalSubPart")). // optional partitioning column(s)
   bucketBy(numBuckets, "colBucket").  // bucketBy can be used with partitionBy only with saveAsTable, see SPARK-19256
   format("parquet").
   mode("overwrite").                   //  Accepted save modes are 'overwrite', 'append', 'ignore', 'error', 'errorifexists', 'default'
   save("filePathandName")             // you can use saveAsTable as an alternative
```
  
- Example of how to write and compacting the output to just 1 file per partition
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
   repartition(num_partitions, col("my_repartition_column")).
   sortWithinPartitions(col("me_repartition_column"), col("additional_orderby_column")).
   write.
   mode("overwrite").
   partitionBy("my_repartition_column")  // optional, if you use this, each partition will be in a separate folder
   format(data_format).
   option("compression", compression_type).
   save(f"{path}/table_name")
)
```
  
### Parquet configuration options
Apache Parquet offers a variety of configurable parameters, enhancing its integration and performance with Spark. For a comprehensive list of these parameters, see the
[Apache Parquet Parameters Documentation.](https://github.com/apache/parquet-mr/blob/master/parquet-hadoop/README.md)

Parquet configuration parameters can be integrated within Spark in several ways:
  - As DataFrame Writer/Reader Options
    - Example: `.option("parquet.block.size", 128*1024*1024")`
  - As Spark Configuration Parameters:
    - Example: `--conf spark.hadoop.parquet.block.size=128*1024*1024`
  - Important: Use the `spark.hadoop` prefix for Hadoop configurations passed via Spark.
  - These options can also be set programmatically during Spark Session creation.
  - Alternatively, configurations can be stored in `spark-defaults.conf`.

Specific Spark DataFrame Configurations for Parquet
The Spark DataFrame reader and writer also support a limited number of options for Parquet configuration. 
For more details, refer to the
[Spark documentation](https://spark.apache.org/docs/latest/sql-data-sources-parquet.html#data-source-option)
on Parquet Data Source Options.

Key configurations include:

There are also specific configurations for the Spark DataFrame reader and Writer that apply to reading/writing 
Parquet too. Some relevant Spark configurations for providing support for large files:  
- Read: 
  - `spark.conf.set("spark.sql.files.maxPartitionBytes", ..)` (default 128 MB) can be used to configure how to pack multiple partitions, relevant for large files with multiple rowgroups
  -  `spark.sql.files.minPartitionNum` the suggested (not guaranteed) minimum number of split file partitions
  - `spark.sql.files.maxPartitionNum` (Spark 3.5.0 and higher) the suggested (not guaranteed) maximum number of split file partitions.
- Write: 
  - `spark.conf.set("spark.sql.files.maxRecordsPerFile", ...)` defaults to 0, use if you need to limit size of files being written
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

### Discovering Parquet Version
The Parquet file format is constantly evolving, incorporating additional metadata to support emerging features.
Each Parquet file embeds the version information within its metadata, reflecting the Parquet version used during
its creation.

**Importance of Version Awareness:**

**Compatibility Considerations:** When working with Parquet files generated by older versions of Spark and 
its corresponding Parquet library, it's important to be aware that certain newer features may not be supported.
For instance, column indexes, which are available in the Spark DataFrame Parquet writer from version 3.2.0, might not be present in files created with older versions.    

**Upgrading for Enhanced Features:** Upon upgrading your Spark version, it's beneficial to also update the metadata 
in existing Parquet files. This update allows you to utilize the latest features introduced in newer versions of 
Parquet.


#### Checking the Parquet File Version:
The following sections will guide you on how to check the Parquet version used in your files, ensuring that 
you can effectively manage and upgrade your Parquet datasets.
This format provides a structured and detailed approach to understanding and managing Parquet file versions,
emphasizing the importance of version compatibility and the process of upgrading.

- Details at [**Tools for Parquet Diagnostics**](Tools_Parquet_Diagnostics.md)

- **parquet-cli**
  - example: `hadoop jar parquet-cli/target/parquet-cli-1.13.1-runtime.jar org.apache.parquet.cli.Main meta <path>/myParquetFile`

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
- **Spark extension library**  
  The [spark-extension library](https://github.com/G-Research/spark-extension/blob/master/PARQUET.md) allows to query Parquet metadata using Apache Spark.  
  Example:
  ```
  bin/spark-shell --packages uk.co.gresearch.spark:spark-extension_2.12:2.11.0-3.5

  import uk.co.gresearch.spark.parquet._
  spark.read.parquetMetadata("...path..").show()
  spark.read.parquetBlockColumns(...path..").show()
  ```

### Updating Parquet File Versions

Upgrading your Parquet files to a newer version can be achieved by copying them using a more recent version of Spark.
This section covers the steps to convert your Parquet files to an updated version.

Conversion Method:  

**Using Recent Spark Versions:** To update Parquet files, read them with a newer version of Spark and then save 
them again. This process effectively updates the files to the Parquet version used by that Spark release.  
For instance, using Spark 3.5.0 will allow you to write files in Parquet version 1.13.1.   

**Approach Note:** This method is somewhat brute-force as there isn't a direct mechanism solely for upgrading
Parquet metadata.

**Practical Example:**
Copying and converting Parquet version by reading and re-writing, applied to the TPCDS benchmark:  
```
bin/spark-shell --master yarn --driver-memory 4g --executor-memory 50g --executor-cores 10 --num-executors 20 --conf spark.sql.shuffle.partitions=400

val inpath="/project/spark/TPCDS/tpcds_1500_parquet_1.10.1/"
val outpath="/project/spark/TPCDS/tpcds_1500_parquet_1.13.1/"
val compression_type="snappy" // may experiment with "zstd"

// we need to do this in two separate groups: partitioned and non-partitioned tables

// copy the **partitioned tables** of the TPCDS benchmark
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

### Parquet 1.12 New Features for Spark 3.2 and Higher
Spark versions 3.2 and 3.3 incorporate Parquet v1.12.x, bringing several significant enhancements 
over previous versions. For Spark 3.5.0, Parquet is upgraded to version 1.13.1. 
These updates introduce new features that improve performance and security.

Key Features in Parquet 1.12:  
**Column Indexes:**  
- Purpose: Column indexes are designed to optimize the execution of filter predicates in specific scenarios.
- Default State: Enabled by default, these indexes enhance query performance by facilitating efficient data filtering.

**Bloom Filters:**
- Function: Bloom filters are implemented to boost the efficiency of executing certain types of filter operations.
- Default State: They are turned off by default and can be enabled as needed.

**Encryption:**
- Security Enhancement: Parquet 1.12 introduces columnar encryption, providing an added layer of security for sensitive data.
- Further Information: Details about columnar encryption in Parquet can be found in [Spark Documentation.](https://spark.apache.org/docs/latest/sql-data-sources-parquet.html#columnar-encryption)  


## Spark filter push down and Parquet column indexes

When scanning Parquet files with Spark using a filter (for example a "where" condition in Spark SQL)
Spark will try to optimize the physical plan by pushing down the filter to Parquet.  
The techniques available with Parquet files are:
- **Partition pruning** if your (set of) files is partitioned, and your filter is on the partitioning column.
  - typically this means that your table is stored on the storage system (HDFS, S3, etc) on a nested folder 
  structure with folder names like <partition_column_name=value>
- **Predicate push down** at the Parquet row group level. 
  - This will use statistics (min and max value) stored for each column with row group granularity 
  (the default row group size is 128 MB)
  - Column chunk dictionaries may be available with dictionary encoding   
- Additional structures introduced in Parquet 1.11 and available when using Spark 3.2.0 and higher are column and offset indexes
  - **column and offset indexes** store statistics (including min and max values) at the granularity of the Parquet page.
  They make possible predicate push down at the page level, which has a default size is 1 MB,
  that is a much finer granularity than the row group size.
- **Sorting data**: the use of column statistics, both at row group and page level (column index), 
  is typically much more effective when data is stored sorted in the Parquet files, this limits the range of values
  in a given page or row group, as opposed to have to deal with a set of values that span across the full range in the table.
  - consider sorting your data when writing Parquet files, the extra work at write time can pay dividend at read time (see also the example below) 
- **Bloom filters** are another structure introduced in recent versions of Parquet that can be used to improve the execution of filter predicates,
  more on this later in this document

## Example: Spark using Parquet column indexes

**Test dataset and preparation**  

- The Parquet test file used below `parquet112file_sorted` is extracted from the TPCDS benchmark table
  [web_sales](https://github.com/apache/spark/blob/master/sql/core/src/test/scala/org/apache/spark/sql/TPCDSSchema.scala#L162)
- the table (parquet file) contains data sorted on the column ws_sold_time_sk
- it's important that the data is sorted, this groups together values in the filter column "ws_sold_time_sk", if the values
  are scattered the column index min-max statistics will have a wide range and will not be able to help with skipping data 
- the sorted dataset has been created using
  `spark.read.parquet("path + "web_sales_piece.parquet").sort("ws_sold_time_sk").coalesce(1).write.parquet(path + "web_sales_piece_sorted_ws_sold_time_sk.parquet")`
- **Download the test data:**
  - Retrieve the test data using `wget`, a web browser, or any method of your choosing
  - [web_sales_piece.parquet](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Parquet_Tests/web_sales_piece.parquet)   
  - [web_sales_piece_sorted_ws_sold_time_sk.parquet](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Parquet_Tests/web_sales_piece_sorted_ws_sold_time_sk.parquet)

**Run the tests**  

1. **Fast** (reads only 20k rows):  
   Spark will read the Parquet using a filter and makes use of **column and offset indexes**:
```
bin/spark-shell

val path = "./" 
val df = spark.read.parquet(path + "web_sales_piece_sorted_ws_sold_time_sk.parquet")

// Read the file using a filter, this will use column and offset indexes
val q1 = df.filter("ws_sold_time_sk=28801")
val plan = q1.queryExecution.executedPlan
q1.collect

// Use Spark metrics to see how many rows were processed
// This is also available for the WebUI in graphical form
val metrics = plan.collectLeaves().head.metrics
metrics("numOutputRows").value

res: Long = 20000
```
The result shows that only 20000 rows were processed, this corresponds to processing just a few pages, as opposed to 
reading and processing the entire file.
This is made possible by the use of the min-max value statistics in the column index for column ws_sold_time_sk.  
Column indexes are created by default in Spark version 3.2.x and higher.

2. **Slow** (reads 2M rows):  
   Same as above but this time we disable the use of column indexes.  
   Note this is also what happens if you use Spark versions prior to Spark 3.2.0 (notably Spark 2.x) to read the file.  
```
bin/spark-shell

val path = "./"
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
This example runs more slowly than the example below and in general performs more work (uses more CPU cycles and
reads more data from the filesystem).


### Diagnostics and Internals of Column and Offset Indexes

Column indexes in Parquet are key structures designed to optimize filter performance during data reads. 
They are particularly effective for managing and querying large datasets.

### Key Aspects of Column Indexes:
- **Purpose and Functionality:** Column indexes offer statistical data (minimum and maximum values) 
  at the page level, facilitating efficient filter evaluation and optimization.
- **Default Activation:** By default, column indexes are enabled to ensure optimal query performance.
- **Granularity Insights:** While column indexes provide page-level statistics, similar statistics are also
  available at the row group level. Typically, a row group is approximately 128MB, contrasting with pages usually
  around 1MB.
- **Customization Options:** Both rowgroup and page sizes are configurable, offering flexibility to tailor data
  organization. For further details, see [Parquet Configuration Options](#parquet-configuration-options).

### Complementary Role of Offset Indexes:
- **Association with Column Indexes:** Offset indexes work in tandem with column indexes and are stored in the
  file's footer in Parquet versions 1.11 and above.
- **Scanning Efficiency:** A key benefit of these indexes is their role in data scanning. When filters are not
  applied in Parquet file scans, the footers with column index data can be efficiently skipped, enhancing the
  scanning process.

### Additional Resources:
For an in-depth explanation of column and offset indexes in Parquet, consider reading this
[detailed description](https://github.com/apache/parquet-format/blob/master/PageIndex.md).

The integration of column and offset indexes significantly improves Parquet's capability in efficiently 
handling large-scale data, especially in scenarios involving filtered reads. 
Proper understanding and utilization of these indexes can lead to marked performance improvements 
in data processing workflows.

### Tools to drill down on column index metadata in Parquet files

- **parquet-cli**
  - example: `hadoop jar target/parquet-cli-1.13.1-runtime.jar org.apache.parquet.cli.Main column-index -c ws_sold_time_sk <path>/my_parquetfile`
  - More details on how to use parquet-cli at [Tools for Parquet Diagnostics](Tools_Parquet_Diagnostics.md)

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

---

## Bloom filters in Parquet

With the release of Parquet 1.12, there's now the capability to generate and store Bloom filters within the file footer's metadata.
This addition significantly enhances query performance for specific filtering operations. 
Bloom filters are especially advantageous in the following scenarios:  

**High Cardinality Columns:** They effectively address the limitations inherent in using Parquet dictionaries for columns with a vast range of unique values.

**Absent Value Filtering:** Bloom filters are highly efficient for queries that filter based on values likely to be missing from
the table or DataFrame. This efficiency stems from the characteristic of Bloom filters where false positives 
(erroneously concluding that a non-existent value is present) are possible, but false negatives 
(failing to identify an existing value) do not occur.

For a comprehensive understanding and technical details of implementing Bloom filters in Apache Parquet, 
refer to the [official documentation on bloom filters in Apache Parquet](https://github.com/apache/parquet-format/blob/master/BloomFilter.md)

### Configuration

Important configurations for writing bloom filters in Parquet files are:
```
.option("parquet.bloom.filter.enabled","true") // write bloom filters for all columns, default is false
.option("parquet.bloom.filter.enabled#column_name", "true") // write bloom filter for the given column
.option("parquet.bloom.filter.expected.ndv#column_name", num_values) // tuning for bloom filters, ndv = number of distinct values
.option("parquet.bloom.filter.max.bytes", 1024*1024) // The maximum number of bytes for a bloom filter bitset, default 1 MB
```

### Write Parquet files with Bloom filters

This is an example of how to read a Parquet file without bloom filter (for example because it had been created with 
an older version of Spark/Parquet) and add the bloom filter, with additional tuning of the bloom filter parameters
for one of the columns:
```
val df = spark.read.parquet("<path>/web_sales")
df.coalesce(1).write.option("parquet.bloom.filter.enabled","true").option("parquet.bloom.filter.expected.ndv#ws_sold_time_sk", 25000).parquet("<myfilepath")
```

### Example: Checking I/O Performance in Parquet: With and Without Bloom Filters
Understanding the impact of using bloom filters on I/O performance during Parquet file reads can be important 
for optimizing data processing. This example outlines the steps to compare I/O performance when reading Parquet
files, both with and without the utilization of bloom filters.

**This example uses Parquet bloom filters to improve Spark read performance**  

**1. Prepare the test table**
```

bin/spark-shell
val numDistinctVals=1e6.toInt
val df=sql(s"select id, int(random()*100*$numDistinctVals) randomval from range($numDistinctVals)")
val path = "./"

// Write the test DataFrame into a Parquet file with a Bloom filter
df.coalesce(1).write.mode("overwrite").option("parquet.bloom.filter.enabled","true").option("parquet.bloom.filter.enabled#randomval", "true").option("parquet.bloom.filter.expected.ndv#randomval", numDistinctVals).parquet(path + "spark320_test_bloomfilter")

// Write the same DataFrame in Parquet, but this time without Bloom filters 
df.coalesce(1).write.mode("overwrite").option("parquet.bloom.filter.enabled","false").parquet(path + "spark320_test_bloomfilter_nofilter")

// use the OS (ls -l) to compare the size of the files with bloom filter and without
// in my test (Spark 3.5.0, Parquet 1.13.1) it was 10107275 with bloom filter and 8010077 without

:quit
```

**2. Read data using the Bloom filter, for improved performance**

```
bin/spark-shell

val path = "./"
val df =spark.read.option("parquet.filter.bloom.enabled","true").parquet(path + "spark320_test_bloomfilter")
val q1 = df.filter("randomval=1000000") // filter for a value that is not in the file
q1.collect

// print I/O metrics
org.apache.hadoop.fs.FileSystem.printStatistics()

// Output
FileSystem org.apache.hadoop.fs.RawLocalFileSystem: 1091611 bytes read, ...

:quit
```

**3. Read disabling the Bloom filter (this will read more data from the filesystem and have worse performance)**  
```
bin/spark-shell

val path = "./"
val df =spark.read.option("parquet.filter.bloom.enabled","false").parquet(path + "spark320_test_bloomfilter")
val q1 = df.filter("randomval=1000000") // filter for a value that is not in the file
q1.collect

// print I/O metrics
org.apache.hadoop.fs.FileSystem.printStatistics()

// Output
FileSystem org.apache.hadoop.fs.RawLocalFileSystem: 8299656 bytes read, ...
```

### Reading Parquet Bloom Filter Metadata with Apache Parquet Java API
To extract metadata about the bloom filter from a Parquet file using the Apache Parquet Java API in spark-shell,
follow these steps:

1. Initialize the File Path:  
   Define the full path of your Parquet file.  
   `val fullPathUri = java.net.URI.create("<my_file_path>")`
2. Create Input File:  
   Utilize HadoopInputFile to create an input file from the specified path.
   ```
   val in = org.apache.parquet.hadoop.util.HadoopInputFile.fromPath(
            new org.apache.hadoop.fs.Path(fullPathUri), 
            spark.sessionState.newHadoopConf()
            )
   ```
3. Open Parquet File Reader:  
   Open the Parquet file reader for the input file.  
   ```
   val pf = org.apache.parquet.hadoop.ParquetFileReader.open(in)
   ```
4. Retrieve Blocks and Columns:  
   Extract the blocks from the file footer and then get the columns from the first block.  
   ````
   val blocks = pf.getFooter.getBlocks
   val columns = blocks.get(0).getColumns
   ```
5. Read Bloom Filter:  
Finally, read the bloom filter from the first column.
`val bloomFilter = pf.readBloomFilter(columns.get(0))`

By following these steps, you can successfully read the bloom filter metadata from a Parquet file using the Java API
in the spark-shell environment.

---
### Vectorized Parquet reader for complex datatypes 
Feature added in Spark 3.3.0
Spark extends the vectorized Parquet reader for complex datatypes.
In Spark 3.4.0 and higher the configuration is on by default.
Configuration:
`--conf spark.sql.parquet.enableNestedColumnVectorizedReader=true`

The performance gain can be high, in the examples with 
[Physics array data at this link](../Spark_Physics#1-dimuon-mass-spectrum-analysis)
the execution time goes from about 30 seconds to 10 seconds when using the vectorized reader.

Caveat: this can lead to high memory use in case of large complex data types (arrays)

### Spark hidden metadata columns for Parquet reader

Feature added in Spark 3.3.0
```
val df=spark.read.parquet("/tmp/testparquet1")

df.select("_metadata.file_path", "_metadata.file_name","_metadata.file_size", "_metadata.file_modification_time").show(2,false)
```
Spark 3.5.0 introduces 2 additional metadata columns: `_metadata.file_block_start` and `_metadata.file_block_length`

### Push down aggregates
Feature added in Spark 3.3.0
Default is false, when true, aggregates will be pushed down to Parquet for optimization
`--conf spark.sql.parquet.aggregatePushdown=true`

### Enable matching schema columns by field id

Feature added in Spark 3.3.0, see [SPARK-38094](https://issues.apache.org/jira/browse/SPARK-38094)
Default is false, when true, Parquet readers will first use the field ID to determine which Parquet columns to read.
It enables matching columns by field id for supported DWs like iceberg and Delta.
`--conf spark.sql.parquet.fieldId.read.enabled=true`


### Anticipating Lazy Materialization: Enhancing Performance in Spark
I'm eagerly awaiting the implementation of a significant improvement that promises to boost performance: Lazy Materialization for Parquet Read Performance Improvement. This enhancement is currently being tracked under the issue:

[SPARK-42256](https://issues.apache.org/jira/browse/SPARK-42256): Lazy Materialization for Parquet Read Performance Improvement
This feature aims to optimize data reading in Spark, particularly for Parquet formatted data, potentially leading to substantial improvements in processing efficiency and speed.
