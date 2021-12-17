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
  - example: hadoop jar parquet-cli/target/parquet-cli-1.12.2-runtime.jar org.apache.parquet.cli.Main meta <path>/myParquetFile`
  - see also [Tools for Parquet Diagnostics](../Tools_Parquet_Diagnostics.md)

- **Hadoop API** ...


## Convert Parquet files to a newer version using Spark
 - here how to convert to newer Parquet version with Spark

## Column indexes
What are they good for
Example
