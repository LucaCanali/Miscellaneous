# SparkHistogram package in Scala
Use with Apache Spark for generating data histograms using the Spark DataFrame API.  
Currently, the package contains only two functions covering some of the most common and low-complexity use cases.  
  - computeHistogram
  - computeWeightedHistogram 

```
import ch.cern.sparkhistogram.Histogram   
val hist = Histogram(spark)

  /**
   * This is a function to compute the count/frequency histogram of a given DataFrame column
   *
   * @param col column name on which to compute the histogram
   * @param min min: minimum value in the histogram
   * @param max maximum value in the histogram
   * @param bins number of histogram buckets to compute
   * @param df the dataframe with the data to compute
   * @return Output DataFrame
   * Output DataFrame
   * ----------------
   *  bucket: the bucket number, range from 1 to bins (included)
   *  value: midpoint value of the given bucket
   *  count: number of values in the bucket
   */
  def computeHistogram(col: String, min: Long, max: Long, bins: Long)(df: DataFrame): DataFrame= {
```
```
  /**
   * This is a function to compute the weighted histogram of a given DataFrame column.
   * A weighted histogram is a generalization of a frequency histogram.
   *
   * @param value_col column name on which to compute the histogram
   *                  the column needs to be of numeric type
   * @param weight_col numeric-type column with the weights,
   *                   the bucket value is computed as sum of weights.
   *                   If all weight are set to 1, you get a frequency histogram
   * @param min min: minimum value in the histogram
   * @param max maximum value in the histogram
   * @param bins number of histogram buckets to compute
   * @param df the dataframe with the data to compute
   * @return Output DataFrame
   * Output DataFrame
   * ----------------
   *  bucket: the bucket number, range from 1 to bins (included)
   *  value: midpoint value of the given bucket
   *  count: weighted sum of the number of values in the bucket
   */
  def computeWeightedHistogram(value_col: String, weight_col: String,
                               min: Long, max: Long, bins: Long)(df: DataFrame): DataFrame= {

```

## Build the jar with sbt
`sbt clean package`

## Examples
Run from the Spark shell. Requires Spark 3.1.0 or higher.  
`bin/spark-shell --jars <path>/target/scala-2.12/sparkhistogram_2.12-0.1.jar`

```
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

```
// Example 2 weighted histogram
import ch.cern.sparkhistogram.Histogram

val hist = Histogram(spark)

val num_events = 100
val scale = 100
val seed = 4242
val seed2 = 4243

val df = spark.sql(s"select random($seed) * $scale as random_value, random($seed2) as weight from range($num_events)")

val histogram = df.transform(hist.computeWeightedHistogram("random_value", "weight", -20, 90, 11))

histogram.show

+------+-----+------------------+
|bucket|value|      weighted_sum|
+------+-----+------------------+
|     1|-15.0|               0.0|
|     2| -5.0|               0.0|
|     3|  5.0|2.3311284945146147|
|     4| 15.0| 4.076542801479973|
|     5| 25.0|  8.18499877878322|
|     6| 35.0| 5.270321110145988|
|     7| 45.0| 5.581395504223541|
|     8| 55.0|3.4259555156362604|
|     9| 65.0| 3.160802943654561|
|    10| 75.0| 7.896726387145422|
|    11| 85.0| 4.783329763967291|
+------+-----+------------------+
```

