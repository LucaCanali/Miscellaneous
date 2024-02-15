#!/usr/bin/env python

from setuptools import setup, find_packages

description = "TPCDS_PySpark is a TPC-DS workload generator implemented in Python designed to run at scale using Apache Spark."

long_description = """
TPCDS_PySpark is a TPC-DS workload generator written in Python and designed to run at scale using Apache Spark.  
A key feature of this tool is that it collects and reports performance metrics using [sparkMeasure](https://github.com/LucaCanali/sparkMeasure),
a performance monitoring library for Apache Spark.  

## Motivations and goals
- Set up a Spark performance lab 
  - Run TPC-DS workloads at scale and study Spark performance
  - Learn about collecting and analyzing Spark performance data, including timing and metrics measurements
  - Learn about Spark performance and optimization
- Compare performance across different Spark configurations and system configurations

Author and contact: Luca.Canali@cern.ch

## Getting started
You can start using TPCDS_PySpark by running the tool as a standalone Python script, from the command line, or by using the TPCDS class to run TPCDS workloads from your Python code.
The tool runs also on notebooks, for example Colab.

1. **Get started Python script:** [getstarted.py](Labs_and_Notes/getstarted.py)
2. **Get started Notebooks:**  
[<img src="https://raw.githubusercontent.com/googlecolab/open_in_colab/master/images/icon128.png" height="50"> TPCDS_PySpark get-started on Colab](https://colab.research.google.com/github/LucaCanali/Miscellaneous/blob/master/Performance_Testing/TPCDS_PySpark/Labs_and_Notes/TPCDS_PySpark_getstarted.ipynb)  
[<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/250px-Jupyter_logo.svg.png" height="50"> TPCDS_PySpark get-started](Labs_and_Notes/TPCDS_PySpark_getstarted.ipynb)

## Installation and requirements:
```
pip install tpcds_pyspark
pip install pyspark
pip install sparkmeasure
pip install pandas
```

## Command line:
```
# Download the test data
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/tpcds_10.zip
unzip -q tpcds_10.zip

# 1. Run the tool for a minimal test
tpcds_pyspark_run.py -d tpcds_10 -n 1 -r 1 --queries q1,q2

# 2. run all queries with default options
./tpcds_pyspark_run.py -d tpcds_10 

# 3. A more complex example, run all queries on a YARN cluster and save the metrics to a file
spark-submit --master yarn --conf spark.log.level=error  --conf spark.executor.cores=8 \
             --conf spark.executor.memory=32g --conf spark.driver.memory=4g \
             --conf spark.driver.extraClassPath=tpcds_pyspark/spark-measure_2.12-0.23.jar \ 
             --conf spark.dynamicAllocation.enabled=false --conf spark.executor.instances=4 \
              tpcds_pyspark_run.py -d HDFS_PATH/tpcds_100 -o ./tpcds_100_out.cvs
```

## API mode:
```
# Get the tool
# pip install tpcds_pyspark 

# Download the test data
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/tpcds_10.zip
unzip -q tpcds_10.zip

from tpcds_pyspark import TPCDS

tpcds = TPCDS(num_runs=1, queries_repeat_times=1, queries=['q1','q2'])
tpcds.map_tables()

tpcds.run_TPCDS()
tpcds.print_test_results()
```

## Usage:
Use it as a script or as an API from Python.
Script:
```
tpcds_pyspark_run.py --help

options:
  -h, --help            show this help message and exit
  --data_path DATA_PATH, -d DATA_PATH
                        Path to the data folder with TPCDS data used for testing. Default: tpcds_10
  --data_format DATA_FORMAT
                        Data format of the data used for testing. Default: parquet
  --num_runs NUM_RUNS, -n NUM_RUNS
                        Number of runs, the TPCS workload will be run this number of times. Default: 2
  --queries_repeat_times QUERIES_REPEAT_TIMES, -r QUERIES_REPEAT_TIMES
                        Number of repetitions, each query will be run this number of times for each run. Default: 3
  --sleep_time SLEEP_TIME, -s SLEEP_TIME
                        Time in seconds to sleep before each query execution. Default: 1
  --queries QUERIES, -q QUERIES
                        List of TPCDS queries to run. Default: all
  --queries_exclude QUERIES_EXCLUDE, -x QUERIES_EXCLUDE
                        List of queries to exclude from the running loop. Default: None
  --output_file OUTPUT_FILE, -o OUTPUT_FILE
                        Optional output file, this will contain the collected metrics details in csv format
  --cluster_output_file CLUSTER_OUTPUT_FILE, -c CLUSTER_OUTPUT_FILE
                        Optional, save the collected metrics to a csv file using Spark, use this to save to HDFS or S3
  --run_using_metastore
                        Run TPCDS using tables defined in metastore tables instead of temporary views. See also --create_metastore_tables to define the tables.
                        Default: False
  --create_metastore_tables
                        Create metastore tables instead of using temporary views. Default: False
  --create_metastore_tables_and_compute_statistics
                        Create metastore tables and compute table statistics to use with Spark CBO. Default: False
```

## Use TPCDS PySpark as an API from Python:

- Use the TPCDS class to run TPCDS workloads from your Python code:
  - `pip install tpcds_pyspark`
  - `from tpcds_pyspark import TPCDS`

**API description: TPCDS**
- **TPCDS(data_path, data_format, num_runs=2, queries_repeat_times, queries, sleep_time)**
  - Defaults: data_path="./tpcds_10", data_format="parquet", num_runs=2, queries_repeat_times=3,
              queries=tpcds_queries, queries_exclude=[], sleep_time=1
- data_path: path to the Parquet folder with TPCDS data used for testing
- data_format: format of the TPCDS data, default: "parquet"
- num_runs: number of runs, the TPCS workload will be run this number of times. Default: 2
- queries_repeat_times: number of repetitions, each query will be run this number of times for each run. Default: 3
- queries: list of TPCDS queries to run
- queries_exclude: list of queries to exclude from the running loop
- sleep_time: time in seconds to sleep before each query execution. Default: 1
- Example: tpcds = TPCDS(data_path="tpcds_10", queries=['q1', 'q2'])

TPCDS main class methods:
- **map_tables:** map the TPCDS tables to the Spark catalog
  - map_tables(self, define_temporary_views=True, define_catalog_tables=False): 
  - this is a required step before running the TPCDS workload
  - Example: tpcds.map_tables()
- **run_TPCDS:** run the TPCDS workload
  - as side effect it populates the following class attributes: self.metadata, self.grouped, self.aggregated
  - Example: results = tpcds.run_TPCDS() 
- print_test_results(output_file=None): print the collected and aggregated metrics to stdout or to a file on the local filesystem
    containing the metadata, metrics grouped by query name and agregated metrics
- save_with_spark: save the collected metrics to a cluster filesystem (HDFS, S3) using Spark
  - save_with_spark(file_path): 
  - Example: tpcds.save_with_spark("HDFS_or_S3_path/my_test_metrics.csv") 
- compute_table_statistics: compute table statistics for the TPCDS tables (optional)
  - compute_table_statistics(collect_column_statistics=True)
  - use only when mapping tables to the Spark catalog (metastore) and when the statistics are not available
  - Example: tpcds.compute_table_statistics()

## Output
- The tool will print to stdout the collected metrics, including timing and metrics measurements.
- It will also print metadata, metrics grouped by query name and aggregated metrics
- Save the collected metrics to a local csv files: `-o my_test_metrics.csv`
   - this will save 4 files: the raw metrics, metadata, metrics grouped by query name, and aggregated metrics
- Optionally, save the collected metrics to a cluster filesystem (HDFS, S3) using Spark: `--cluster_output_file PATH/my_test_metrics.csv` 


## Download TPCDS Data
The tool requires TPCDS benchmark data in parquet or other format. 
For convenience the TPCDS benchmark data at scale 10G can be downloaded:
```
# TPCDS scale 10G
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/tpcds_10.zip
unzip -q tpcds_10.zip

# TPCDS scale 100G
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/tpcds_100.zip
unzip tpcds_100.zip
```

## Generate TPCDS data with a configurable scale factor

- You can generate Spark TPCDS benchmark data at any scale using the following steps:
  - Download and build the Spark package from https://github.com/databricks/spark-sql-perf
  - Download and build tpcds-kit for generating data from https://github.com/databricks/tpcds-kit
  
### Source, labs and examples
- [TPCDS PySpark on GitHub](https://github.com/LucaCanali/Miscellaneous/tree/master/Performance_Testing/TPCDS_PySpark)
"""

setup(name='TPCDS_PySpark',
    version='1.0.5',
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Luca Canali',
    author_email='luca.canali@cern.ch',
    url='https://github.com/LucaCanali/Miscellaneous/tree/master/Performance_Testing/TPCDS_PySpark',
    license='Apache License, Version 2.0',
    include_package_data=True,
    scripts=['tpcds_pyspark/tpcds_pyspark_run.py'],
    packages=find_packages(),
    package_data={
        'tpcds_pyspark': ['spark-measure_2.12-0.24.jar', 'Queries/*'],
    },
    zip_safe=False,
    python_requires='>=3.9',
    install_requires=[],
    classifiers=[
    'Programming Language :: Python :: 3',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: Apache Software License',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Education',
    'Development Status :: 4 - Beta',
    ]
    )
