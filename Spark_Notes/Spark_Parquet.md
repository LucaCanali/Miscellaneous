# Spark and Parquet

Apache Parquet is one of the preferred data formats when using Apache Spark.  
Basic use:
```
val df = spark.read.parquet("file path") // read
df.write.mode("overwrite").parquet("file path") // write
```
[Link to the Spark docs](https://spark.apache.org/docs/latest/sql-data-sources-parquet.html)

## Configuration options
Options:
```
val compression_type="zstd" // snappy is default
.option("compression", compression_type)
.option("parquet.block.size",128*1024*1024)
```
[link with a list of Apache Parquet parameters](https://github.com/apache/parquet-mr/blob/master/parquet-hadoop/README.mdhttps://github.com/apache/parquet-mr/blob/master/parquet-hadoop/README.md`)

## Spark 3.2 and Parquet 1.12 new features

Spark 3.2 comes with Parquet v1.12, Spark 3.1 and 2.4 have Spark 1.10.
Notable Parquet features newly available in Spark 3.2 are:

- Column indexes
  - desc and link to doc
- Bloom filters
    - desc and link to doc
- Encryption
   - desc and link to doc

## Parquet version
You need to write parquet files with the Parquet version 1.12 or higher to use those features.
With Spark this means using Spark 3.2 or higher when available.

How to check the Parquet version used for a given file:
- 

You can convert existing files:
 - here how to convert to newer Parquet version with Spark

## Column indexes
What are they good for
Example
