# How to generate histograms at scale with Apache Spark DataFrame API and with Spark SQL

This details a few basic methods and tools to generate histograms using the Spark DataFrame API and with Spark SQL.
Disambiguation: we refer here to computing histograms of the DataFrame data, rather than histograms of the columns' statistics used by the cost based optimizer.   

## Contents
  - **Notebook examples:**
    - [frequency histograms using the DataFrame API](Spark_Histograms/Spark_DataFrame_Frequency_Histograms.ipynb)
    - [weighted histograms using the DataFrame API](Spark_Histograms/Spark_DataFrame_Weighted_Histograms.ipynb)
    - [frequency histograms using Spark SQL](Spark_Histograms/Spark_SQL_Frequency_Histograms.ipynb)
  - How to generate frequency histograms using Spark DataFrame functions or Spark SQL:
    - [Python version](#python-version-generate-histograms-with-a-spark-dataframe-function) and the sparkhistogram package 
    - [Scala version](#scala-version-generate-histograms-with-a-spark-dataframe-function)
    - [SQL version](#sql-version-generate-histograms-with-spark-sql)
  - [Other solutions](#Other-solutions)
    - Spark RDD histograms
    - Histogrammer

## Notes on the techniques used:
  - The solutions discussed here are for 1-dimensional fixed-width histograms
  - Use the package, sparkhistogram, together with PySpark for generating data histograms using the Spark DataFrame API.
    Currently, the package contains only two functions covering some of the most common and low-complexity use cases.
  - The proposed techniques are wrappers around [width_bucket](https://spark.apache.org/docs/latest/api/sql/index.html#width_bucket)  
    - this makes them applicable to a large range of data and database systems, that implement the width_bucket function
  - The histograms are generated with DataFrame operations in Spark, this allows to run them at scale.  
  - When handling small amounts of data, you can evaluate the alternative of fetching all the data
     into the driver and then use standard libraries to generate histograms, such as
     [Pandas histogram](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.hist.html) or
     [numpy histogram](https://numpy.org/doc/stable/reference/generated/numpy.histogram.html)
     or [boost-histogram](https://boost-histogram.readthedocs.io/en/latest/)
  - Link with additional techniques for [generating histograms with SQL](http://www.silota.com/docs/recipes/sql-histogram-summary-frequency-distribution.html)
  
## (Python version) Generate histograms with a Spark DataFrame function

This is an example of how to generate frequency histograms using PySpark and the helper
function in the package [sparkhistogram](https://github.com/LucaCanali/Miscellaneous/blob/master/Spark_Notes/Spark_Histograms/python/sparkhistogram/histogram.py)
```
# requires the package sparkhistogram
! pip install sparkhistogram

# import the computeHistogram function 
from sparkhistogram import computeHistogram

# Generate a DataFrame with toy data for demo purposes
num_events = 100
scale = 100
seed = 4242
df = spark.sql(f"select random({seed}) * {scale} as random_value from range({num_events})")

# Compute the histogram using the computeHistogram function
hist = computeHistogram(df, "random_value", -20, 90, 11)

# Alternative syntax,  compute the histogram using transform on the DataFrame
# requires Spark 3.3.0 or higher
hist = df.transform(computeHistogram, "random_value", -20, 90, 11)

# this triggers the computation as show() is an action
hist.show()

+------+-----+-----+
|bucket|value|count|
+------+-----+-----+
|     1|-15.0|    0|
|     2| -5.0|    0|
|     3|  5.0|    6|
|     4| 15.0|   10|
|     5| 25.0|   15|
|     6| 35.0|   12|
|     7| 45.0|    9|
|     8| 55.0|    7|
|     9| 65.0|   10|
|    10| 75.0|   16|
|    11| 85.0|    7|
+------+-----+-----+
```

This is ho computeHistogram is defined:
```
def computeHistogram(df: "DataFrame", value_col: str, min: float, max: float, bins: int) -> "DataFrame"

Parameters
----------
df: the dataframe with the data to compute
value_col: column name on which to compute the histogram
min: minimum value in the histogram
max: maximum value in the histogram
bins: number of histogram buckets to compute

Output DataFrame
----------------
bucket: the bucket number, range from 1 to bins (included)
value: midpoint value of the given bucket
count: number of values in the bucket
```


## (Scala version) Generate histograms with a Spark DataFrame function

1. You can use the [sparkhistogram package](scala/README.md) as in this example:

```
Run from the Spark shell. Requires Spark 3.1.0 or higher.  
bin/spark-shell --jars <path>/target/scala-2.12/sparkhistogram_2.12-0.1.jar


// Example 1 frequency histogram
import ch.cern.sparkhistogram.Histogram

val hist = Histogram(spark)

val num_events = 100
val scale = 100
val seed = 4242

val df = spark.sql(s"select random($seed) * $scale as random_value from range($num_events)")

df.show(5)

// compute the histogram
val histogram = df.transform(hist.computeHistogram("random_value", -20, 90, 11))

// alternative syntax
// val histogram = hist.computeHistogram("random_value", -20, 90, 11)(df)

histogram.show

+------+-----+-----+
|bucket|value|count|
+------+-----+-----+
|     1|-15.0|    0|
|     2| -5.0|    0|
|     3|  5.0|    6|
|     4| 15.0|   10|
|     5| 25.0|   15|
|     6| 35.0|   12|
|     7| 45.0|    9|
|     8| 55.0|    7|
|     9| 65.0|   10|
|    10| 75.0|   16|
|    11| 85.0|    7|
+------+-----+-----+
```
2. As an alternative you can define the `computeHistogram` (or `computeWeightedHistogram`) function in your code,
as in this example: 
```
Run from the Spark shell. Requires Spark 3.1.0 or higher.  
bin/spark-shell

import org.apache.spark.sql.{DataFrame, Dataset}

def computeHistogram(col: String, min: Long, max: Long, bins: Long)(df: DataFrame): DataFrame= {
  val step = (max - min) / bins
  // this will be used to fill in for missing buckets, i.e. buckets with no corresponding values
  val df_buckets= spark.sql(s"select id+1 as bucket from range($bins)")
    
  df.
    selectExpr(s"width_bucket($col, $min, $max, $bins) as bucket").
    groupBy("bucket").
    count().
    join(df_buckets, Seq("bucket"), "right_outer"). // add missing buckets and remove buckets out of range
    selectExpr("bucket", s"$min + (bucket - 1/2) * $step as value", // use center value of the buckets
               "nvl(count, 0) as count").  // buckets with no values will have a count of 0
    orderBy("bucket")         
}

// generate some data for demo purposes

val num_events = 100
val scale = 100
val seed = 4242

val df = spark.sql(s"select random($seed) * $scale as random_value from range($num_events)")

df.show(5)

// compute the histogram
val histogram = df.transform(computeHistogram("random_value", -20, 90, 11))

histogram.show()
```

## (SQL version) Generate histograms using Spark SQL

This is  an example of how to generate histograms using Spark SQL.  
Note this uses Python's formatted strings to fill in parameters into the query text.
Run with PySpark/Spark version 3.1.0 or higher.

```
# Generate a DataFrame with some data for demo purposes and map it to a temporary view

num_events = 100
scale = 100
seed = 4242

df = spark.sql(f"select random({seed}) * {scale} as random_value from range({num_events})")

# map the df DataFrame to the t1 temporary view so it can be used with Spark SQL
df.createOrReplaceTempView("data")

table_name = "data" # table or temporary view containing the data
value_col = "random_value" # column name on which to compute the histogram
min = -20  # min: minimum value in the histogram
max = 90   # maximum value in the histogram
bins = 11  # number of histogram buckets to compute
step = (max - min) / bins

histogram = spark.sql(f"""
with hist as (
  select 
    width_bucket({value_col}, {min}, {max}, {bins}) as bucket,
    count(*) as cnt
  from {table_name}
  group by bucket
  ),
buckets as (
  select id+1 as bucket from range({bins})
)
select
    bucket, {min} + (bucket - 1/2) * {step} as value,
    nvl(cnt, 0) as count
from hist right outer join buckets using(bucket)
order by bucket
""")

# Output DataFrame description
# ----------------------------
# bucket: the bucket number, range from 1 to bins (included)
# value: midpoint value of the given bucket
# count: number of values in the bucket        

# this triggers the computation as show() is an action
histogram.show()
```

## Other solutions

- Note that Spark RDD API has a histogram function [see doc](https://spark.apache.org/docs/latest/api/python/pyspark.html)
  It can be used with Spark Dataframes as a workaround as in:
```
sql("select cast(id as double) from t1").rdd.map(x => x(0).asInstanceOf[Double]).histogram(3)

res1: (Array[Double], Array[Long]) = (Array(0.0, 3.0, 6.0, 9.0),Array(3, 3, 4))
```

- Histogrammar is a package for creating histograms
  - See https://histogrammar.github.io
  - See example to use histogrammar with Spark at https://github.com/histogrammar/histogrammar-python#example-notebooks