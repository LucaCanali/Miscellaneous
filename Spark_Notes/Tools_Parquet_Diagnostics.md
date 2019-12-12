# Parquet Diagnostics Tools

This is extracted from the blog post [Diving into Spark and Parquet Workloads, by Example](http://externaltable.blogspot.com/2017/06/diving-into-spark-and-parquet-workloads.html)

Here a some examples of usage of a few tools and utilities that I find useful to investigate Parquet files.
relevant links on internals of Parquet  and their metadata are
 - the documentation at (https://parquet.apache.org/documentation/latest)
 - Also the Parquet source code has many additional details in the form of comments to the code. See for example: [ParquetOutputFormat.java](https://github.com/Parquet/parquet-mr/blob/master/parquet-hadoop/src/main/java/parquet/hadoop/ParquetOutputFormat.java)

Some of the main points about Parquet internals that I want to highlight are:
- Hierarchically, a Parquet file consists of one or more "row groups". A row group contains data grouped ion "column chunks", one per column. Column chunks are structured in pages. Each column chunk contains one or more pages.
- Parquet files have several metadata structures, containing among others the schema, the list of columns and details about the data stored there, such as name and datatype of the columns, their size, number of records and basic statistics as minimum and maximum value (for datatypes where support for this is available, as discussed in the previous section).
- Parquet can use compression and encoding. The user can choose the compression algorithm used, if any. By default Spark uses snappy. 
- Parquet can store complex data types and support nested structures. This is quite a powerful feature and it goes beyond the simple examples presented in this post.


## Parquet-tools

Parquet-tools is part of the main Apache Parquet repository, you can download it from  https://github.com/apache/parquet-mr/releases
The tests described here are based on Parquet version 1.8.2, released in January 2017. 

Tip: you can build and package the jar for parquet-tools with:
```
cd parquet-mr-apache-parquet-1.8.2/parquet-tools
mvn package -DskipTests
```

You can use parquet tools to examine the metadata of a Parquet file on HDFS using: "hadoop jar <path_to_jar> meta <path_to_Parquet_file>".  Other commands available with parquet-tools, besides "meta" include: cat, head, schema, meta, dump, just run parquet-tools with -h option to see the syntax.
This is an example of how to use the tool to read files located on HDFS:

```
$ echo "read metadata from a Parquet file in HDFS"
$ hadoop jar parquet-mr-apache-parquet-1.8.2/parquet-tools/target/parquet-tools-1.8.2.jar meta TPCDS/tpcds_1500/store_sales/ss_sold_date_sk=2452621/part-00077-57653b27-17f1-4069-85f2-7d7adf7ab7df.snappy.parquet
```

The output lists several details of the file metadata:
file path, parquet version used to write the file (1.8.2 in this case), additional info (Spark Row Metadata in this case):

```
file:                  hdfs://XXX.XXX.XXX/user/YYY/TPCDS/tpcds_1500/store_sales/ss_sold_date_sk=2452621/part-00077-57653b27-17f1-4069-85f2-7d7adf7ab7df.snappy.parquet
creator:               parquet-mr version 1.8.2 (build c6522788629e590a53eb79874b95f6c3ff11f16c)
extra:                 org.apache.spark.sql.parquet.row.metadata = {"type":"struct","fields":[{"name":"ss_sold_time_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ss_item_sk","type":"integer","nullable":true,"metadata":{}},
...omitted in the interest of space... 
{"name":"ss_net_profit","type":"decimal(7,2)","nullable":true,"metadata":{}}]}
```
Additionally metadata about the schema:

```
file schema:           spark_schema
--------------------------------------------------------------
ss_sold_time_sk:       OPTIONAL INT32 R:0 D:1
ss_item_sk:            OPTIONAL INT32 R:0 D:1
ss_customer_sk:        OPTIONAL INT32 R:0 D:1
ss_cdemo_sk:           OPTIONAL INT32 R:0 D:1
ss_hdemo_sk:           OPTIONAL INT32 R:0 D:1
ss_addr_sk:            OPTIONAL INT32 R:0 D:1
ss_store_sk:           OPTIONAL INT32 R:0 D:1
ss_promo_sk:           OPTIONAL INT32 R:0 D:1
ss_ticket_number:      OPTIONAL INT32 R:0 D:1
ss_quantity:           OPTIONAL INT32 R:0 D:1
ss_wholesale_cost:     OPTIONAL INT32 O:DECIMAL R:0 D:1
ss_list_price:         OPTIONAL INT32 O:DECIMAL R:0 D:1
ss_sales_price:        OPTIONAL INT32 O:DECIMAL R:0 D:1
ss_ext_discount_amt:   OPTIONAL INT32 O:DECIMAL R:0 D:1
ss_ext_sales_price:    OPTIONAL INT32 O:DECIMAL R:0 D:1
ss_ext_wholesale_cost: OPTIONAL INT32 O:DECIMAL R:0 D:1
ss_ext_list_price:     OPTIONAL INT32 O:DECIMAL R:0 D:1
ss_ext_tax:            OPTIONAL INT32 O:DECIMAL R:0 D:1
ss_coupon_amt:         OPTIONAL INT32 O:DECIMAL R:0 D:1
ss_net_paid:           OPTIONAL INT32 O:DECIMAL R:0 D:1
ss_net_paid_inc_tax:   OPTIONAL INT32 O:DECIMAL R:0 D:1
ss_net_profit:         OPTIONAL INT32 O:DECIMAL R:0 D:1
```
Metadata about the row groups:

![Metadata about the row groups](https://3.bp.blogspot.com/-7ISYeX6pN1o/WVP2qF2mKSI/AAAAAAAAE8k/oXvfaYHOjZAO2SVSF7WlRnhPISjsaj8wQCLcBGAs/s1600/Metadata_fig%2B_annotated.PNG)

Note: If you want to investigate further, you can also dump information down to the page level using the command: parquet-tools command "dump --disable-data" on the Parquet file of interest.

## Parquet_reader

Parquet_reader This is another utility that can help you navigate the internals and metadata of Parquet files. In particular parquet-cpp displays the statistics associated with Parquet columns and is useful to understand predicate push down.
Parquet_reader is a utility distributed with the Parquet-cpp project.
You can download it from https://github.com/apache/parquet-cpp/releases. This has since moved to Apache Arrow, see: https://github.com/apache/parquet-cpp
The tests reported here have been run using version 1.1.0 released in May 2017.
Tips: You can build the project with: "cmake ." followed by "make". After that you can find the utility parquet_reader in the folder build/latest.

This is an example of how to use parquet_reader to browse file metadata. The tool works on filesystem data, so I have copied the parquet file from HDFS to local filesystem before running this:

```./parquet_reader --only-metadata part-00077-57653b27-17f1-4069-85f2-7d7adf7ab7df.snappy.parquet```

File metadata:  similarly to the case of parquet-tools you can find the list of columns and their data types. Note however that DECIMAL columns are not identified.

```
File Name: part-00077-57653b27-17f1-4069-85f2-7d7adf7ab7df.snappy.parquet
Version: 0
Created By: parquet-mr version 1.8.2 (build c6522788629e590a53eb79874b95f6c3ff11f16c)
Total rows: 2840100
Number of RowGroups: 2
Number of Real Columns: 22
Number of Columns: 22
Number of Selected Columns: 22
Column 0: ss_sold_time_sk (INT32)
Column 1: ss_item_sk (INT32)
Column 2: ss_customer_sk (INT32)
Column 3: ss_cdemo_sk (INT32)
Column 4: ss_hdemo_sk (INT32)
Column 5: ss_addr_sk (INT32)
Column 6: ss_store_sk (INT32)
Column 7: ss_promo_sk (INT32)
Column 8: ss_ticket_number (INT32)
Column 9: ss_quantity (INT32)
Column 10: ss_wholesale_cost (INT32)
Column 11: ss_list_price (INT32)
Column 12: ss_sales_price (INT32)
Column 13: ss_ext_discount_amt (INT32)
Column 14: ss_ext_sales_price (INT32)
Column 15: ss_ext_wholesale_cost (INT32)
Column 16: ss_ext_list_price (INT32)
Column 17: ss_ext_tax (INT32)
Column 18: ss_coupon_amt (INT32)
Column 19: ss_net_paid (INT32)
Column 20: ss_net_paid_inc_tax (INT32)
Column 21: ss_net_profit (INT32)
```

Row group metadata: here a snippet for the metadata relative the first row group. It contains the total size in bytes and the number of rows.

```--- Row Group 0 ---
--- Total Bytes 154947976 ---
  Rows: 2840100---
```

Column chunk metadata: similarly to the case of parquet-tools you can find details on the number of rows and the compressed/uncompressed size. In addition parquet_reader shows the statistics of Minimum and Maximum values. Also the number of null values are reported, while distinct values appears to be 0 (not populated).

```
Column 0
, Values: 2840100, Null Values: 66393, Distinct Values: 0
  Max: 75599, Min: 28800
  Compression: SNAPPY, Encodings: RLE PLAIN_DICTIONARY BIT_PACKED
  Uncompressed Size: 5886233, Compressed Size: 2419027
Column 1
, Values: 2840100, Null Values: 0, Distinct Values: 0
  Max: 32000, Min: 1
  Compression: SNAPPY, Encodings: RLE PLAIN_DICTIONARY BIT_PACKED
  Uncompressed Size: 5040503, Compressed Size: 5040853
Column 2
, Values: 2840100, Null Values: 66684, Distinct Values: 0
  Max: 4599961, Min: 15
  Compression: SNAPPY, Encodings: RLE PLAIN_DICTIONARY BIT_PACKED
  Uncompressed Size: 7168827, Compressed Size: 4200678
...
```

Notably, there are no statistics for columns of type DECIMAL. This has implications for filter push down, as discussed earlier in this post. See for example:

```
...
Column 10
, Values: 2840100  Statistics Not Set
  Compression: SNAPPY, Encodings: RLE PLAIN_DICTIONARY BIT_PACKED
  Uncompressed Size: 5113188, Compressed Size: 5036313
Column 11
, Values: 2840100  Statistics Not Set
  Compression: SNAPPY, Encodings: RLE PLAIN_DICTIONARY BIT_PACKED
  Uncompressed Size: 5500119, Compressed Size: 5422519
...
```