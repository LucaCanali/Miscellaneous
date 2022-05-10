# How to generate histograms at scale with Apache Spark DataFrame API and with Spark SQL

This details a few methods and tools to generate histograms using the Spark DataFrame API.  
Disambiguation: we refer here to computing histograms of the DataFrame data, rather than histograms of the columns statistics used by the cost based optimizer.   

## Contents
  - **Notebook examples:**
    - [frequency histograms using the DataFrame API](Spark_Histograms/Spark_DataFrame_Frequency_Histograms.ipynb)
    - [frequency histograms using the Spark SQL](Spark_Histograms/Spark_SQL_Frequency_Histograms.ipynb)
    - [weighted histograms using the DataFrame API](Spark_Histograms/Spark_DataFrame_Weighted_Histograms.ipynb)
  - How to generate frequency histograms with a Spark DataFrame function
    - [Python version](#python-version-generate-histograms-with-a-spark-dataframe-function) 
    - [Scala version](#scala-version-generate-histograms-with-a-spark-dataframe-function)
    - [SQL version](#sql-version-generate-histograms-with-spark-sql)
  - [Other solutions](#Other-solutions)
    - Spark RDD histograms
    - Histogrammer

## Techniques:
  - The solutions discussed here are for 1-dimensional fixed-width histograms
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

```
def computeHistogram(df: "DataFrame", value_col: str, min: int, max: int, bins: int) -> "DataFrame":
    """ This is a dataframe function to compute the count/frequecy histogram of a column
        
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
    """
    step = (max - min) / bins
    # this will be used to fill in for missing buckets, i.e. buckets with no corresponding values
    df_buckets = spark.sql(f"select id+1 as bucket from range({bins})")
    
    histdf = (df
              .selectExpr(f"width_bucket({value_col}, {min}, {max}, {bins}) as bucket")
              .groupBy("bucket")
              .count()
              .join(df_buckets, "bucket", "right_outer") # add missing buckets and remove buckets out of range
              .selectExpr("bucket", f"{min} + (bucket - 1/2) * {step} as value", # use center value of the buckets
                          "nvl(count, 0) as count") # buckets with no values will have a count of 0
              .orderBy("bucket")
             )
    return histdf

# Generate a DataFrame with some data for demo purposes
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
```

## (Scala version) Generate histograms with a Spark DataFrame function

```
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

## (SQL version) Generate histograms with Spark SQL

Note this uses PySpark f-string to fill in parameters

```
table_name = "t1" # table or temporary view containing the data
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

- histogrammar package  
  - Histogrammar is a package for creating histograms
  - See https://histogrammar.github.io
  - See example to use histogrammar with Spark at https://github.com/histogrammar/histogrammar-python#example-notebooks