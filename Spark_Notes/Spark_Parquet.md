# Apache Spark and Parquet

Data formats make an important part of data platforms.
Apache Parquet is one of the preferred data formats when using Apache Spark for data analysis.
This comes from several reasons, some of the most important are that Parquet is a columnar format
that allows compression, encoding and several additional features to support filter pushdown and partitioning.

### Parquet 1.12 new features and Spark 3.2

Spark 3.2 uses Parquet v1.12 (previous releases, Spark 3.1, 3.0 and 2.4 use Parquet Spark 1.10)
Notable Parquet features newly available in Spark 3.2 are:

- Column indexes
  - desc and link to doc
- Bloom filters
    - desc and link to doc
- Encryption
   - desc and link to doc

### Basic use of the DataFrame reader and writer with Parquet:
A quick recap of the basics of using Parquet with Spark.
For more details see [Spark datasource documentation](https://spark.apache.org/docs/latest/sql-data-sources-parquet.html)
```
val df = spark.read.parquet("file path") // read
df.write.mode("overwrite").parquet("file path") // write
```

### Configuration options
There are several configurable parameters for the Parquet datasources, see:
[link with a list of Apache Parquet parameters](https://github.com/apache/parquet-mr/blob/master/parquet-hadoop/README.md`)

A few notable options for Apache Spark Parquet DataFrame writer:
```
.option("compression", compression_type)      // compression algorithm, default when using Spark is snappy, use none for no compression
.option("parquet.block.size", 128*1024*1024)  // Parquet rowgroup (block) size, default 128 MB
.option("parquet.page.size", 1024*1024)       // parquet page size, default 1 MB
.option("parquet.page.row.count.limit)        // the maximum number of rows per page, default 20000
.option("parquet.bloom.filter.enabled","true") // write bloomfilters, default is false
.option("parquet.bloom.filter.expected.ndv#column_name", num_values) // tuning for bloom filters
.option("parquet.enable.dictionary","true")   // enable/disable dictionary encoding, default is true 
```

A few notable options for Apache Spark Parquet DataFrame reader:
```
.option("parquet.filter.bloom.enabled","true")       // use bloom filters (default: true)
.option("parquet.filter.columnindex.enabled","true") // use column indexes (default: true)
.option("parquet.filter.dictionary.enabled","true")  // use row group dictionary filtering (default: true)
.option("parquet.filter.stats.enabled", "true")      // use row row group stats filtering (default: true)
```

### Parquet version

As Parquet format evolves, more metadata is made available which is used by new features.
The Parquet version used to write a given file is stored in the metadata.  
If you use Parquet files written with old versions of Spark (say Spark 2.x) and therefore old Parquet libraries,
you may not be able to use features introduced in recent versions, like column indexes available for Spark DataFrame Parquet writer as of version 3.2.0.  
When you upgrade Spark you may want to upgrade the metadata in your Parquet files too.

**How to check the Parquet version:**  

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

**How convert Parquet files to a newer version by copying them using Spark**
 - Use a recent Spark to read the source Parquet files and save them with the Parquet version
  used by Spark. For example with Spark 3.2.0 you can write files in Parquet version 1.12.1
 - Example of how to copy Parquet files for the TPCDS benchmark
```
bin/spark-shell --master yarn --driver-memory 4g --executor-memory 50g --executor-cores 10 --num-executors 20 --conf spark.sql.shuffle.partitions=400

val inpath="/project/spark/TPCDS/tpcds_1500_parquet_1.10.1/"
val outpath="/project/spark/TPCDS/tpcds_1500_parquet_1.12.1/"
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

## Spark Filter pushdown to Parquet improved with column indexes and bloom filters

When scanning Parquet files with Spark using a filter (e.g. a "where" condition in Spark SQL)
Spark will try to optimize the physical by pushing down the filter
The techniques available with Parquet files are:
- Partition pruning if your (set of) files is partitioned, and your filter is on the partitioning column.
- Predicate push down at the row group level. 
  - This will use statistics (min and max value) stored for each column
  - Column chunk dictionaries may be available with dictionary encoding   
- Additional structures introduced in Parquet 1.11 are column and offset indexes
  - these store statistics (including min and max values) allowing predicate
  push down at the page level (that is a much finer granularity than row group).
- Parquet 1.12 introduces the option to generate and store bloom filters in Parquet metadata on the file footer.
- Note: the use of column statistics, both at row group and page level (column index), 
  is typically more effective when data that is stored in Parque file sorted,
  as opposed to have large ranges of data for each page or rowgroup.

Examples:

1. Spark reading with a filter that makes use of column and offset indexes:
```
val df =spark.read.parquet("/home/luca/test/testParquetFile/parquet112file_sorted")
val q1 = df.filter("ws_sold_time_sk=28801")
val plan = q1.queryExecution.executedPlan
q1.collect
val metrics = plan.collectLeaves().head.metrics
metrics("numOutputRows").value
```
The result is that only 20000 rows are read, this corresponds to a single page,
see also column index details for column ws_sold_time_sk in the previous paragraph.


2. Same as above but this time we disable the use of column indexes
(this is also what happens if you use Spark versions older than 3.2.0)
```
val df =spark.read.option("parquet.filter.columnindex.enabled","false").parquet("/home/luca/test/testParquetFile/parquet112file_sorted")
val q1 = df.filter("ws_sold_time_sk=28801")
val plan = q1.queryExecution.executedPlan
q1.collect
val metrics = plan.collectLeaves().head.metrics
metrics("numOutputRows").value
```
The result is that all the rows in the row group (340689 rows) are read as Spark 
cannot push the filter down to page level.

### Column and offset indexes

Column indexes are structures that can improve the performance of filters on Parquet files.  
Column indexes provide stats (min and max values) on the data at the page granularity, which can be used to evaluate filters. Similar statistics are available
at rowgroup level, however a rowgroup is typically 128MB in size, while pages are typically 1MB
(both are configurable).  
Column indexes and their sibling, offset indexes, are stored in the footer of Parquet files version 1.11 and above.  
See a detailed [description of column and offset indexes in Parquet at this link](https://github.com/apache/parquet-format/blob/master/PageIndex.md)

**Tools to drill down on column indexe metadata in Parquet files**

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
Parquet has introduced bloom filters in version 1.12.
Bloom filters improve the performance of filter predicates.
They are particularly useful with high cardinality columns to overcome the limitations
of using Parquet dictionaries. 
You can find the details [of bloom filters in Apache Parquet at this link](https://github.com/apache/parquet-format/blob/master/BloomFilter.md)

**Configuration**

Two important configurations for writing bloom filters in Parquet files are:
```
.option("parquet.bloom.filter.enabled","true") // write bloom filters for all columns, default is false
.option("parquet.bloom.filter.enabled#column_name") // write bloom filter for the given column
.option("parquet.bloom.filter.expected.ndv#column_name", num_values) // tuning for bloom filters, ndv = number of distinct values
```

This is an example of how to read a Parquet file without bloom filter (for example because created with 
an older version of Spark/Parquet) and add the bloom filter, with additional tuning for one of the columns:
```
val df = spark.read.par
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

For demo purposes this example disables the use of dictionary and column index filters, which is an optimization that improves filter execution too`.option("parquet.filter.dictionary.enabled","false")`
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
