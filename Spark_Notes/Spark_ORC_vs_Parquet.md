# Comparing ORC and Parquet when used with Spark
Apache ORC and Parquet are optimized data formats for data analysis and Apache Spark is optimized to use them.  
There are many similarities in their use and configuration.
  
Cheat sheet Parquet vs ORC architecture.  
Reference: Parquet version 1.12 and ORC version 1.7

| Parquet                                                                                                                | ORC                                                                           | Comment                                                                                                                |
|------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| https://parquet.apache.org/docs/                                                                                       | https://orc.apache.org/specification/ORCv1/                                   | Reference Links                                                                                                        |
| Files -> row groups -> pages<br/>                                                                                      | Files -> stripes                                                              | Key data layout structures                                                                                             |
| Data in organized in column chunks                                                                                     | Same as Parquet: data in organized by column                                  | Columnar data formats                                                                                                  |
| Data statistics are stored at the rowgroup level and page level                                                        | Similar to Parquet: data statistics are stored at the stripe and row set level | Index-type structures for improved filter execution (min, max, number of rows, and number of null values are provided) |
| Bloom filter support                                                                                                   | Same as Parquet                                                               | Bloom filters improve the performance of certain filter predicates (speed up value not in a set searches)              |
| Support for filter push down                                                                                           | Same as Parquet                                                               | Query engines like Spark can offload filters to the data source| 
| Data is encoded, algorithms include dictionary encoding, run length enconding, and delta encoding                      | Same as Parquet                                                               | Encoding improves data storage                                                                                         |
| Support compression, default algorithm when using Spark is snappy, also supports zlib, ZStandard and other codecs | Same as Parquet                                                               | Compression |
| Support all data types in Spark + complex data types: arrays, structs and maps                                         | Same as Parquet                                                               | Extensive data type support|
  
----------
  
Cheat sheet Parquet vs ORC when using Apache Spark  
Reference: Spark 3.3.x, Parquet version 1.12.x, and ORC version 1.7.x

| Parquet                                                                                                                                                          | ORC                                                     | Comment                                                             |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|---------------------------------------------------------------------|
| https://spark.apache.org/docs/latest/sql-data-sources-parquet.html                                                                                               | https://spark.apache.org/docs/latest/sql-data-sources-orc.html | Links                                                               |
| `.option("parquet.block.size", 128*1024*1024)`<br/> Parquet rowgroup (block) size, default = 128 MB                                                              | `orc.stripe.size`<br/>Default = 64 MB                   | Rowgroup/stripe size, this is the main unit of parallelism          |
| `.option("parquet.page.size", 1024*1024)` default 1MB<br/>`.option("parquet.page.row.count.limit)`<br/> default 20000                                            | `orc.row.index.stride`<br/>Default 10000                | Lowest granularity for data statistics gathering and filtering      |
 | `.option("compression", "snappy")`<br/>snapppy is default, also support none, ZStandard, zlib and others                                                         | Same as Parquet                                         | Compression                                                         |
| `.option("parquet.bloom.filter.enabled","true")` write bloomfilters, default is false<br/>`.option("parquet.bloom.filter.expected.ndv#column_name", num_values)` | `orc.bloom.filter.columns` and `orc.bloom.filter.fpp` (default 0.05) | Configure bloom filters when writing data with the DataFrame writer |
 | `parquet.encryption.column.keys`, `parquet.encryption.footer.key`                                                                                                | `orc.key.provider`, `orc.encrypt`, `orc.mask`           | Encryption- related parameters                                      |
| `--conf spark.sql.parquet.enableNestedColumnVectorizedReader=true`                                                                                               | `spark.sql.orc.enableNestedColumnVectorizedReader=true`| enable nested column vectorized reader                              |
