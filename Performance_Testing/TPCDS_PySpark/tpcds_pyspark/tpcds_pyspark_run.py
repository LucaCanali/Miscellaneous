#!/usr/bin/env python3

import argparse
from re import split
import sys
from tpcds_pyspark import TPCDS

usage = """
tpcds_pyspark_run.py - A TPCDS workload generator running on Apache Spark.  
The tool runs on Python and PySpark, and is instrumented to collect Spark metrics with sparkMeasure

## Motivations and goals
- TPCDS_PySpark provides tooling for investigating Spark performance. It is designed to be used for: 
  - Running TPC-DS workloads at scale and study Spark performance
  - Learning about collecting and analyzing Spark performance data, including timing and metrics measurements
  - Learning about Spark performance and optimization
  - Comparing performance across different Spark configurations and system configurations

Author and contact: Luca.Canali@cern.ch   

## Getting started

## Installation and dependencies:
 
pip install pyspark
pip install sparkmeasure
pip install tpcds_pyspark
pip install pandas

# Download the test data
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/tpcds_10.zip
unzip -q tpcds_10.zip

Command line:

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
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="TPCDS PySpark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=usage)
    parser.add_argument("--data_path", "-d", action = 'store', required=False, help="Path to the data folder with TPCDS data used for testing. Default: %(default)s", default="tpcds_10")
    parser.add_argument("--data_format", action = 'store', required=False, help="Data format of the data used for testing. Default: %(default)s", default="parquet")
    parser.add_argument("--num_runs", "-n", action = 'store', type = int,  required=False, help="Number of runs, the TPCS workload will be run this number of times. Default: %(default)s", default=2)
    parser.add_argument("--queries_repeat_times", "-r", action = 'store', type = int,  required=False, help="Number of repetitions, each query will be run this number of times for each run. Default: %(default)s", default=3)
    parser.add_argument("--sleep_time", "-s", action = 'store', type = int,  required=False, help="Time in seconds to sleep before each query execution. Default: %(default)s", default=1)
    parser.add_argument("--queries", "-q", action = 'store', required=False, help="List of TPCDS queries to run. Default: %(default)s", default="all")
    parser.add_argument("--queries_exclude", "-x", action = 'store', required=False, help="List of queries to exclude from the running loop. Default: %(default)s", default=None)
    parser.add_argument("--output_file", "-o", action = 'store', required=False, help="Optional output file, this will contain the collected metrics details in csv format", default=None)
    parser.add_argument("--cluster_output_file", "-c", action = 'store', required=False, help="Optional, save the collected metrics to a csv file using Spark, use this to save to HDFS or S3", default=None)
    parser.add_argument("--run_using_metastore", action='store_true', required=False, help="Run TPCDS using tables defined in metastore tables instead of temporary views. See also --create_metastore_tables to define the tables. Default: %(default)s", default=False)
    parser.add_argument("--create_metastore_tables", action='store_true', required=False, help="Create metastore tables instead of using temporary views. Default: %(default)s", default=False)
    parser.add_argument("--create_metastore_tables_and_compute_statistics", action='store_true', required=False, help="Create metastore tables and compute table statistics to use with Spark CBO. Default: %(default)s", default=False)

    args = parser.parse_args()

    data_path = args.data_path
    data_format = args.data_format
    queries_repeat_times = args.queries_repeat_times
    num_runs = args.num_runs
    sleep_time = args.sleep_time
    run_using_metastore = args.run_using_metastore
    create_metastore_tables = args.create_metastore_tables
    create_metastore_tables_and_compute_statistics = args.create_metastore_tables_and_compute_statistics

    # Configure the list of queries to run
    if args.queries == "all":
        queries = TPCDS.tpcds_queries
    else:
        queries = split(r',\s*', args.queries)
    # exclude list if specified
    queries_exclude = split(r',\s*', args.queries_exclude) if args.queries_exclude else []

    # Set up the TPCDS workload generator
    tpcds = TPCDS(data_path, data_format, num_runs, queries_repeat_times, queries, queries_exclude, sleep_time)

    # Get the Spark session
    spark = tpcds.spark

    # This is the standard way of running the workload
    # It maps the tables to temporary views before running the workload
    if not (run_using_metastore or create_metastore_tables or create_metastore_tables_and_compute_statistics):
        tpcds.map_tables(define_temporary_views=True, define_catalog_tables=False)

    # Optionally, create metastore tables and compute statistics
    if create_metastore_tables or create_metastore_tables_and_compute_statistics:
        print("\nCreating metastore tables using the default database for the Spark session")
        print("defined in spark.sql.catalog.spark_catalog.defaultDatabase")
        # Check that spark.sql.catalogImplementation is set to hive
        if spark.conf.get("spark.sql.catalogImplementation") != "hive":
            print("Error: spark.sql.catalogImplementation is not set to hive")
            print("Please set --conf spark.sql.catalogImplementation=hive and re-run the workload")
            print("Exiting...")
            spark.stop()
            sys.exit(1)
        # Map the tables to Spark catalog
        tpcds.map_tables(define_temporary_views=False, define_catalog_tables=True)
        # Optionally, compute table statistics and use Spark CBO
        if create_metastore_tables_and_compute_statistics:
            print("\nComputing table statistics")
            tpcds.compute_table_statistics(collect_column_statistics=False)
        else:
            print("Consider using --create_metastore_tables_and_compute_statistics to use Spark CBO")
        print("Metastore tables created")
        if not run_using_metastore:
            print("Exiting, please restart with the option --run_using_metastore")
            spark.stop()
            sys.exit(0)

    print("Starting TPCDS workload with PySpark")
    print(f"Data path = {data_path}")
    print(f"Queries = {args.queries}")
    print(f"Number of runs = {args.num_runs}")
    print(f"Number of query repeat times = {queries_repeat_times}")
    print(f"Output file = {args.output_file}")
    print(f"Allocating Spark session")

    # Run TPCDS with the tables defined on the metastore
    if run_using_metastore:
        print("\nRunning the workload using TPCDS tables defined in metastore")
        # Check that spark.sql.catalogImplementation is set to hive
        if spark.conf.get("spark.sql.catalogImplementation") != "hive":
            print("Error: spark.sql.catalogImplementation is not set to hive")
            print("Please set --conf spark.sql.catalogImplementation=hive and re-run the workload")
            print("Exiting...")
            spark.stop()
            sys.exit(1)
        # check if stats are there for the table web_sales (just use that one table as representative as a shortcut)
        stats = df=spark.sql("describe table extended web_sales").where("col_name=='Statistics' and data_type like '%rows'")
        if stats == 0:
            print("Note, stats are not gathered for the tables")
            print("Consider running --create_metastore_tables_and_compute_statistics")
        else:
            print("Table stats have been gathered")
        print("\nTo use Spark CBO make sure stats are gathered and the following configurations are enabled.")
        print("Current CBO key configuration values:")
        cbo = spark.conf.get("spark.sql.cbo.enabled")
        hist = spark.conf.get("spark.sql.statistics.histogram.enabled")
        print(f"spark.sql.cbo.enabled = {cbo}")
        print(f"(needed only if columns stats were gathered) spark.sql.statistics.histogram.enabled = {hist}")

    # Run the TPCDS workload and collect the instrumentation data
    tpcds.run_TPCDS()

    # Print the test results and configuration to stdout
    # Test results contain a line for each executed query and detail the collected metrics
    tpcds.print_test_results()

    # Optionally, save the test results and configuration to local filesystem too
    # It runs only if args.output_file is specified, It will store 4 files:
    #   - metrics in args.output_file
    #   - configuration in args.output_file + ".metadata"
    #   - summary statistics grouped per query name in args.output_file + ".grouped"
    #   - aggregated summary statistics in args.output_file + ".aggregated"
    if args.output_file:
        tpcds.print_test_results(args.output_file)
        print("\nSaved the collected metrics to a local filesystem")

    # Save the test results to using Spark.
    # Use to save to a cluster filesystem (HDFS, S3)
    # This runs only if args.cluster_file is specified
    # Note that the files will be saved as folders, with the name of the file being the folder name
    # Note the Python version on the executors and the driver must be the same
    if args.cluster_output_file:
        tpcds.save_with_spark(args.cluster_output_file)
        print("\nSaved the collected metrics to a cluster filesystem using Spark")
