# Parquet Diagnostics Tools

In this doc you can find some examples of tools and utilities that I find useful to investigate Parquet files.  
Relevant links on internals of Parquet and their metadata are
 - Documentation at https://parquet.apache.org/docs/
 - Link with a list of [Apache Parquet configuration options](https://github.com/apache/parquet-mr/blob/master/parquet-hadoop/README.md)
 - Comment in Parquet source code. See for example: [ParquetOutputFormat.java](https://github.com/apache/parquet-mr/blob/master/parquet-hadoop/src/main/java/org/apache/parquet/hadoop/ParquetOutputFormat.java)

Blogs and notes on Spark and Parquet: 
 - [Utilizing Apache Spark with Parquet Format](Spark_Parquet.md)
 - [Diving into Spark and Parquet Workloads, by Example](https://db-blog.web.cern.ch/blog/luca-canali/2017-06-diving-spark-and-parquet-workloads-example) (CERN Blog)
 - [Inspecting Parquet files with Spark](https://www.gresearch.com/blog/article/parquet-files-know-your-scaling-limits/) (G-Research blog) 

Some highlights of Parquet structure that make it a very useful data format for data analysis are:
- Parquet is a columnar data format. 
- Parquet files consist of one or more "row groups", which allow for splitting and parallelizinig the file access. A row group contains data grouped ion "column chunks", one per column. Column chunks are structured in pages. Each column chunk contains one or more pages.
- Parquet files have several metadata structures, containing among others the schema, the list of columns and details about the data stored there, such as name and datatype of the columns, their size, number of records and basic statistics as minimum and maximum value (for datatypes where support for this is available, as discussed in the previous section).
- Parquet can use compression and encoding. The user can choose the compression algorithm used, if any. By default, Spark uses snappy. 
- Parquet can store complex data types and support nested structures. This is quite a powerful feature and it goes beyond the simple examples presented in this post.

---

## Parquet-cli
Parquet-cli is part of the main Apache Parquet repository, you can download it from
https://github.com/apache/parquet-mr/
The tests described here are based on Parquet version 1.13.1, released in May 2023.

Tip: you can build and package the jar for parquet-tools with:
```
cd parquet-mr-apache-parquet-1.13.1/parquet-cli
mvn -DskipTests clean package 
```

Parquet-cli has multiple commands, including: meta to Print a Parquet file's metadata, schema,
column-index to print the column and offset indexes of a Parquet file.

Example:

```
hadoop jar parquet-cli/target/parquet-cli-1.13.1-runtime.jar org.apache.parquet.cli.Main meta <path>/myParquetFile

Created by: parquet-mr version 1.13.1 (build db4183109d5b734ec5930d870cdae161e408ddba)
Properties:
                   org.apache.spark.version: 3.5.0
  org.apache.spark.sql.parquet.row.metadata: {"type":"struct","fields":[{"name":"ws_sold_time_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_ship_date_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_item_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_bill_customer_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_bill_cdemo_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_bill_hdemo_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_bill_addr_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_ship_customer_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_ship_cdemo_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_ship_hdemo_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_ship_addr_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_web_page_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_web_site_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_ship_mode_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_warehouse_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_promo_sk","type":"integer","nullable":true,"metadata":{}},{"name":"ws_order_number","type":"long","nullable":true,"metadata":{}},{"name":"ws_quantity","type":"integer","nullable":true,"metadata":{}},{"name":"ws_wholesale_cost","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_list_price","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_sales_price","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_ext_discount_amt","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_ext_sales_price","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_ext_wholesale_cost","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_ext_list_price","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_ext_tax","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_coupon_amt","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_ext_ship_cost","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_net_paid","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_net_paid_inc_tax","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_net_paid_inc_ship","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_net_paid_inc_ship_tax","type":"decimal(7,2)","nullable":true,"metadata":{}},{"name":"ws_net_profit","type":"decimal(7,2)","nullable":true,"metadata":{}}]}

Schema:
message spark_schema {
  optional int32 ws_sold_time_sk;
  optional int32 ws_ship_date_sk;
  optional int32 ws_item_sk;
  optional int32 ws_bill_customer_sk;
  optional int32 ws_bill_cdemo_sk;
  optional int32 ws_bill_hdemo_sk;
  optional int32 ws_bill_addr_sk;
  optional int32 ws_ship_customer_sk;
  optional int32 ws_ship_cdemo_sk;
  optional int32 ws_ship_hdemo_sk;
  optional int32 ws_ship_addr_sk;
  optional int32 ws_web_page_sk;
  optional int32 ws_web_site_sk;
  optional int32 ws_ship_mode_sk;
  optional int32 ws_warehouse_sk;
  optional int32 ws_promo_sk;
  optional int64 ws_order_number;
  optional int32 ws_quantity;
  optional int32 ws_wholesale_cost (DECIMAL(7,2));
  optional int32 ws_list_price (DECIMAL(7,2));
  optional int32 ws_sales_price (DECIMAL(7,2));
  optional int32 ws_ext_discount_amt (DECIMAL(7,2));
  optional int32 ws_ext_sales_price (DECIMAL(7,2));
  optional int32 ws_ext_wholesale_cost (DECIMAL(7,2));
  optional int32 ws_ext_list_price (DECIMAL(7,2));
  optional int32 ws_ext_tax (DECIMAL(7,2));
  optional int32 ws_coupon_amt (DECIMAL(7,2));
  optional int32 ws_ext_ship_cost (DECIMAL(7,2));
  optional int32 ws_net_paid (DECIMAL(7,2));
  optional int32 ws_net_paid_inc_tax (DECIMAL(7,2));
  optional int32 ws_net_paid_inc_ship (DECIMAL(7,2));
  optional int32 ws_net_paid_inc_ship_tax (DECIMAL(7,2));
  optional int32 ws_net_profit (DECIMAL(7,2));
}


Row group 0:  count: 340689  67.76 B records  start: 4  total: 22.015 MB
--------------------------------------------------------------------------------
                          type      encodings count     avg size   nulls   min / max
ws_sold_time_sk           INT32     S _ R     340689    0.53 B     45      "29" / "86399"
ws_ship_date_sk           INT32     S _ R     340689    0.88 B     42      "2450819" / "2450938"
ws_item_sk                INT32     S   _     340689    4.00 B     0       "1" / "32000"
ws_bill_customer_sk       INT32     S _ R     340689    0.59 B     39      "93" / "4599972"
ws_bill_cdemo_sk          INT32     S _ R     340689    0.58 B     41      "59" / "1920782"
ws_bill_hdemo_sk          INT32     S _ R     340689    0.34 B     38      "1" / "7200"
ws_bill_addr_sk           INT32     S _ R     340689    0.58 B     43      "82" / "2299974"
ws_ship_customer_sk       INT32     S _ R     340689    0.59 B     53      "285" / "4599966"
ws_ship_cdemo_sk          INT32     S _ R     340689    0.59 B     47      "40" / "1920782"
ws_ship_hdemo_sk          INT32     S _ R     340689    0.34 B     44      "1" / "7200"
ws_ship_addr_sk           INT32     S _ R     340689    0.58 B     43      "61" / "2299983"
ws_web_page_sk            INT32     S _ R     340689    0.88 B     40      "1" / "208"
ws_web_site_sk            INT32     S _ R     340689    0.63 B     38      "1" / "32"
ws_ship_mode_sk           INT32     S _ R     340689    0.63 B     44      "1" / "20"
ws_warehouse_sk           INT32     S _ R     340689    0.38 B     48      "1" / "5"
ws_promo_sk               INT32     S _ R     340689    1.13 B     41      "1" / "375"
ws_order_number           INT64     S _ R     340689    0.67 B     0       "4802" / "89998084"
ws_quantity               INT32     S _ R     340689    0.88 B     42      "1" / "100"
ws_wholesale_cost         INT32     S _ R     340689    1.87 B     45      "1.00" / "100.00"
ws_list_price             INT32     S   _     340689    4.00 B     47      "1.03" / "299.49"
ws_sales_price            INT32     S _ R     340689    2.12 B     40      "0.00" / "296.77"
ws_ext_discount_amt       INT32     S   _     340689    4.00 B     43      "0.00" / "28573.00"
ws_ext_sales_price        INT32     S   _     340689    4.00 B     42      "0.00" / "27868.00"
ws_ext_wholesale_cost     INT32     S   _     340689    4.00 B     43      "1.00" / "10000.00"
ws_ext_list_price         INT32     S   _     340689    4.00 B     41      "1.07" / "29219.00"
ws_ext_tax                INT32     S   _     340689    3.41 B     36      "0.00" / "2249.13"
ws_coupon_amt             INT32     S _ R     340689    1.52 B     36      "0.00" / "22567.27"
ws_ext_ship_cost          INT32     S   _     340689    4.00 B     39      "0.00" / "14064.96"
ws_net_paid               INT32     S   _     340689    4.00 B     48      "0.00" / "27868.00"
ws_net_paid_inc_tax       INT32     S   _     340689    4.00 B     44      "0.00" / "29468.88"
ws_net_paid_inc_ship      INT32     S   _     340689    4.00 B     0       "0.00" / "39811.00"
ws_net_paid_inc_ship_tax  INT32     S   _     340689    4.00 B     0       "0.00" / "40827.99"
ws_net_profit             INT32     S   _     340689    4.00 B     0       "-9894.06" / "18293.00"

```

## PyArrow

Pyarrow has a Parquet reader and can be used to explore metadata.  
From
https://mungingdata.com/pyarrow/parquet-metadata-min-max-statistics/  
see also
https://arrow.apache.org/docs/python/parquet.html#inspecting-the-parquet-file-metadata  

Example:
```
import pyarrow.parquet as pq
parquet_file = pq.ParquetFile('/tmp/a.parquet')
parquet_file.metadata

parquet_file.metadata.row_group(0)
parquet_file.metadata.row_group(0).column(0)
parquet_file.metadata.row_group(0).column(0).statistics
```

## Querying Parquet metadata with Spark

The spark-extension library allows to query Parquet metadata using Apache Spark.
See https://github.com/G-Research/spark-extension/blob/master/PARQUET.md

Example:
```
bin/spark-shell --packages uk.co.gresearch.spark:spark-extension_2.12:2.11.0-3.5

import uk.co.gresearch.spark.parquet._
spark.read.parquetMetadata("...path..").show()
spark.read.parquetBlockColumns(...path..").show()
```

## Parquet-tools (deprecated)

Parquet-tools is part of the main Apache Parquet repository, you can download it from  https://github.com/apache/parquet-mr/releases
The tests described here are based on Parquet version 1.8.2, released in January 2017. 
In more recent versions of Parquet, parquet-tools has been renamed to parquet-tools-deprecated and
parquet-cli (see above) should be used instead.

Tip: you can build and package the jar for parquet-tools with:
```
cd parquet-mr-apache-parquet-1.8.2/parquet-tools
mvn -DskipTests clean package 
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
Additionally, metadata about the schema:

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

## Parquet_reader (deprecated)

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
