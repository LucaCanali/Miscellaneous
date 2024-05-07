"""
computeHistogram is a function to compute the count/frequency histogram of a given DataFrame column.
computeWeightedHistogram is a function to compute the weighted histogram of a given DataFrame column.
A weighted histogram is a generalization of a frequency histogram.
"""

from pyspark.sql.functions import sum
from pyspark.sql import SparkSession


def computeHistogram(df: "DataFrame", value_col: str, min_val: float, max_val: float, bins: int) -> "DataFrame":
    """ This is a function to compute the count/frequency histogram of a given DataFrame column
        
        Parameters
        ----------
        df: the dataframe with the data to compute
        value_col: column name on which to compute the histogram
        min_val: minimum value in the histogram
        max_val: maximum value in the histogram
        bins: number of histogram buckets to compute
        
        Output DataFrame
        ----------------
        bucket: the bucket number, range from 1 to bins (included)
        value: midpoint value of the given bucket
        count: number of values in the bucket        
    """
    # Compute the step size for the histogram
    step = (max_val - min_val) / bins

    # Get the Spark Session handle
    spark = SparkSession.getActiveSession()

    # df_buckets is the range of {bins} buckets as requested by the user
    # It will be used to fill in for missing buckets, i.e. buckets with no corresponding values
    df_buckets = spark.range(bins).selectExpr("id + 1 as bucket")

    # Group user data into buckets and count their population count
    df_grouped = (df
                   .selectExpr(f"width_bucket({value_col}, {min_val}, {max_val}, {bins}) as bucket")
                   .groupBy("bucket")
                   .count()
                 )

    # Join df_buckets with the grouped data to fill in missing buckets
    df_hist = (df_buckets # note this will be typically broadcasted, the order of the join is important
               .join(df_grouped, "bucket", "left_outer") # add missing buckets and remove buckets out of range
               .selectExpr("bucket", f"{min_val} + (bucket - 0.5) * {step} as value",  # use center value of the buckets
                           "nvl(count, 0) as count") # buckets with no values will have a count of 0
               .orderBy("bucket")
              )

    return df_hist


def computeWeightedHistogram(df: "DataFrame", value_col: str, weight_col: str,
                             min_val: float, max_val: float, bins: int) -> "DataFrame":
    """ This is a dataframe function to compute the weighted histogram of a DataFrame column.
        A weighted histogram is a generalization of a frequency histogram.

        Parameters
        ----------
        df: the dataframe with the data to compute
        value_col: column name on which to compute the histogram
                   the column needs to be of numeric type
        weight_col: numeric-type column with the weights,
                    the bucket value is computed as sum of weights.
                    If all weight are set to 1, you get a frequency histogram
        min_val: minimum value in the histogram
        max_val: maximum value in the histogram
        bins: number of histogram buckets to compute

        Output DataFrame
        ----------------
        bucket: the bucket number, range from 1 to bins (included)
        value: midpoint value of the given bucket
        weighted_sum: weighted sum of the number of values in the bucket
    """
    # Compute the step size for the histogram
    step = (max_val - min_val) / bins

    # Get the Spark Session handle
    spark = SparkSession.getActiveSession()

    # df_buckets is the range of {bins} buckets as requested by the user
    # It will be used to fill in for missing buckets, i.e. buckets with no corresponding values
    df_buckets = spark.range(bins).selectExpr("id + 1 as bucket")

    # Group user data into buckets and compute a weighted sum of the values
    df_grouped = (df
                  .selectExpr(f"width_bucket({value_col}, {min_val}, {max_val}, {bins}) as bucket", f"{weight_col}")
                  .groupBy("bucket")
                  .agg(sum(f"{weight_col}").alias("weighted_sum"))  # sum the weights on the weight_col
                 )

    # Join df_buckets with the grouped data to fill in missing buckets
    df_hist = (df_buckets # note this will be typically broadcasted, the order of the join is important
               .join(df_grouped, "bucket", "left_outer") # add missing buckets and remove buckets out of range
               .selectExpr("bucket", f"{min_val} + (bucket - 0.5) * {step} as value",  # use center value of the buckets
                           "nvl(weighted_sum, 0) as weighted_sum")  # buckets with no values will have a sum of 0
               .orderBy("bucket")
               )

    return df_hist
