#!/usr/bin/env python

from setuptools import setup, find_packages

description = "Sparkhistogram contains helper functions for generating data histograms with the Spark DataFrame API."

long_description = """
Use this package, sparkhistogram, together with PySpark for generating data histograms using the Spark DataFrame API.
Currently, the package contains only two functions covering some of the most common and low-complexity use cases.

Use:
- `from sparkhistogram import computeHistogram` -> computeHistogram is a function to compute the count/frequency histogram of a given DataFrame column
- `from sparkhistogram import computeWeightedHistogram` -> computeWeightedHistogram is a function to compute the weighted histogram of a given DataFrame column  

```
def computeHistogram(df: "DataFrame", value_col: str, min_val: float, max_val: float, bins: int) -> "DataFrame"

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
```

## Run this example in the PySpark shell 
Note: requires PySpark version 3.1 or higher.  

`bin/pyspark`

```
# import the helper function to generate the histogram using Spark DataFrame operations
from sparkhistogram import computeHistogram

# generate some toy data
num_events = 100
scale = 100
seed = 4242
df = spark.sql(f"select random({seed}) * {scale} as random_value from range({num_events})")

# define the DataFrame transformation to compute the histogram 
histogram = computeHistogram(df, "random_value", -20, 90, 11) 

# with Spark 3.3.0 and higher you can also use df.transform
# histogram = df.transform(computeHistogram, "random_value", -20, 90, 11)

# fetch and display the (toy) data
histogram.show()

# expected output:
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

More details and notebooks with matplotlib visualization of the histograms at:  
https://github.com/LucaCanali/Miscellaneous/blob/master/Spark_Notes/Spark_DataFrame_Histograms.md
"""

setup(name='sparkhistogram',
    version='0.4',
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Luca Canali',
    author_email='luca.canali@cern.ch',
    url='https://github.com/LucaCanali/Miscellaneous/blob/master/Spark_Notes/Spark_DataFrame_Histograms.md',
    license='Apache License, Version 2.0',
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=[],
    classifiers=[
    'Programming Language :: Python :: 3',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: Apache Software License',
    'Intended Audience :: Developers',
    'Development Status :: 4 - Beta',
    ]
    )
