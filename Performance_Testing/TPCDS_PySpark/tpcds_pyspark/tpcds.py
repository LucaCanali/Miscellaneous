#!/usr/bin/env python3

from datetime import datetime
import pandas as pd
import sys
import time
from importlib.resources import files
from pyspark.sql import SparkSession
from sparkmeasure import StageMetrics

class TPCDS:
    """This implements the TPCDS workload generator with Apache Spark and sparkMeasure
    using PySpark"""

    tpcds_queries = [
        'q1', 'q2', 'q3', 'q4', 'q5', 'q5a', 'q6', 'q7', 'q8', 'q9',
        'q10', 'q10a', 'q11', 'q12', 'q13', 'q14a', 'q14b', 'q14', 'q15',
        'q16', 'q17', 'q18', 'q18a', 'q19', 'q20', 'q21', 'q22', 'q22a',
        'q23a', 'q23b', 'q24', 'q24a', 'q24b', 'q25', 'q26', 'q27', 'q27a',
        'q28', 'q29', 'q30', 'q31', 'q32', 'q33', 'q34', 'q35', 'q35a',
        'q36', 'q36a', 'q37', 'q38', 'q39a', 'q39b', 'q40', 'q41', 'q42',
        'q43', 'q44', 'q45', 'q46', 'q47', 'q48', 'q49', 'q50', 'q51',
        'q51a', 'q52', 'q53', 'q54', 'q55', 'q56', 'q57', 'q58', 'q59',
        'q60', 'q61', 'q62', 'q63', 'q64', 'q65', 'q66', 'q67', 'q67a',
        'q68', 'q69', 'q70', 'q70a', 'q71', 'q72', 'q73', 'q74', 'q75',
        'q76', 'q77', 'q77a', 'q78', 'q79', 'q80', 'q80a', 'q81', 'q82',
        'q83', 'q84', 'q85', 'q86', 'q86a', 'q87', 'q88', 'q89', 'q90',
        'q91', 'q92', 'q93', 'q94', 'q95', 'q96', 'q97', 'q98', 'q99'
    ]

    # List of table names for the TPCDS benchmark
    tpcds_tables = [
        "catalog_returns", "catalog_sales", "inventory", "store_returns",
        "store_sales", "web_returns", "web_sales", "call_center",
        "catalog_page", "customer", "customer_address",
        "customer_demographics", "date_dim", "household_demographics",
        "income_band", "item", "promotion", "reason", "ship_mode",
        "store", "time_dim", "warehouse", "web_page", "web_site"
    ]

    def __init__(self, data_path="./tpcds_10", data_format="parquet",
                 num_runs=2, queries_repeat_times=3, queries=tpcds_queries, queries_exclude=[], sleep_time=1):
        self.data_path = data_path
        self.data_format = data_format
        self.queries = queries
        self.queries_repeat_times = queries_repeat_times
        self.num_runs = num_runs
        self.sleep_time = sleep_time
        self.start_time = None
        self.end_time = None
        self.test_results = None
        self.results_pdf = None
        self.grouped_results_pdf = None

        # Path to the TPCDS queries on the filesystem
        tpcds_pyspark_files = files('tpcds_pyspark')
        self.queries_path = tpcds_pyspark_files.joinpath('Queries') # Path to the TPCDS queries on the filesystem
        # Path to sparkMeasure bundled jar
        # TODO: handle the embedded sparkMeasure jar for scala 2.12 and 2.13 in the same code
        sparkMeasure_jar = tpcds_pyspark_files.joinpath('spark-measure_2.12-0.24.jar')

        print(f"sparkMeasure jar path: {sparkMeasure_jar}")
        print(f"TPCDS queries path: {self.queries_path}")

        # Input validation for the queries and queries_exclude
        # Check that queries is equal or a subset of tpcds_queries
        if not set(queries).issubset(self.tpcds_queries):
            raise ValueError(f"queries must be a subset of {self.tpcds_queries}")
        # Check that queries_exclude is a subset of queries
        if not set(queries_exclude).issubset(self.queries):
            raise ValueError(f"queries_exclude must be a subset of {self.queries}")
        # Subtract queries_exclude from queries, keeping the order of queries
        self.queries_to_run = [query for query in self.queries if query not in queries_exclude]

        # This configures the SparkSession
        # The recommended way is to use spark-submit to launch tpcds_pyspark.py
        # When run directly instead, the SparkSession will be created here using default config.
        self.spark = (
            SparkSession.builder
                .appName("TPCDS PySpark - Run TPCDS queries in PySpark instrumented with sparkMeasure")
                .config("spark.driver.extraClassPath", sparkMeasure_jar)
                .getOrCreate()
             )

    def map_tables(self, define_temporary_views=True, define_catalog_tables=False):
        """Map table data on the filesystem to Spark tables.
        This supports both creating temporary views or metastore catalog tables
        for the tables used in the TPCDS queries.
        This supports all data formats supported by Spark."""

        data_path = self.data_path
        data_format = self.data_format
        spark = self.spark
        tables = self.tpcds_tables

        # Loop through each table name and create a temporary view for it
        if define_temporary_views:
            for table in tables:
                print(f"Creating temporary view {table}")
                table_full_path = data_path + "/" + table
                spark.read.format(data_format).load(table_full_path).createOrReplaceTempView(table)

        # Loop through each table name and create a catalog table for it
        # This will use the default database for the Spark session
        # defined in spark.sql.catalog.spark_catalog.defaultDatabase
        if define_catalog_tables:
            for table in tables:
                # Construct the full path for the table data
                table_full_path = f"{data_path}/{table}"

                # Log the creation of the catalog table
                print(f"Creating catalog table {table}")

                # Drop the table if it already exists to avoid conflicts
                spark.sql(f"DROP TABLE IF EXISTS {table}")

                # Create an external table pointing to the data path
                create_table_sql = f"""
                CREATE EXTERNAL TABLE IF NOT EXISTS {table}
                USING {data_format}
                OPTIONS (path '{table_full_path}')
                """
                spark.sql(create_table_sql)
                #
                # Fix for partitioned tables, this picks up the partitioning schema from the data's folder structure
                try:
                    # Attempt to repair the table
                    repair_command = f"MSCK REPAIR TABLE {table}"
                    spark.sql(repair_command)
                    print("...partitioned table repaired to map the data folder structure")
                except Exception as e:
                    # Handle exceptions, likely due to the table not being partitioned
                    None

    def compute_table_statistics(self, collect_column_statistics=False):
        # Compute statistics on the tables/views
        spark = self.spark
        tables = self.tpcds_tables
        print("Enabling Cost Based Optimization (CBO) and computing statistics")
        for table in tables:
            spark.sql("SET spark.sql.cbo.enabled=true")
            if collect_column_statistics:
                # table stats and column stats collection is very slow, use with caution
                spark.sql("SET spark.sql.statistics.histogram.enabled=true")
                print(f"Computing table and column statistics for {table}")
                spark.sql(f"ANALYZE TABLE {table} COMPUTE STATISTICS FOR ALL COLUMNS")

            else:
                print(f"Computing table statistics for {table}")
                spark.sql(f"ANALYZE TABLE {table} COMPUTE STATISTICS")
                print("Add the following configuration to use the Spark CBO:")
                print("spark.sql.cbo.enabled=true")
        print("\nStatistics collection is complete")
        print("Add the following configurations to use the Spark CBO:")
        print("spark.sql.cbo.enabled=true")
        if collect_column_statistics:
            print("spark.sql.statistics.histogram.enabled=true")

    def run_TPCDS(self):
        """Run the TPCDS queries and return the instrumentation data.
        Requires the Spark session to be already created and configured.
        Requires the TPCDS data to be mapped to Spark tables ot temporary views,
        See map_tables() method.
        """

        spark = self.spark
        queries_path = str(self.queries_path)
        queries_repeat_times = self.queries_repeat_times
        queries_to_run = self.queries_to_run
        num_runs = self.num_runs
        sleep_time = self.sleep_time

        # List to store the job timing and metrics measurements
        instrumentation = []
        stagemetrics = StageMetrics(spark)
        self.start_time = time.ctime()

        # External loop to run the query set multiple times (configurable)
        for run_id in range(num_runs):
            # Read and run the queries from the queries_path
            for query in queries_to_run:
                with open(queries_path + "/" + query + ".sql", 'r') as f:
                    # Read the query text from the file
                    query_text = f.read()

                    # Internal loop to run the same query multiple times (configurable)
                    for i in range(queries_repeat_times):

                        print(f"\nRun {run_id} - query {query} - attempt {i} - starting...")

                        # Add a configurable sleep time (default 1 sec) before each query execution
                        time.sleep(sleep_time)
                        # Set the job group and description to the query name
                        spark.sparkContext.setJobGroup("TPCDS", query)
                        # Start the stage metrics collection
                        startime_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        stagemetrics.begin()

                        # Run the query and send the output to a noop sink
                        spark.sql(query_text).write.format("noop").mode("overwrite").save()

                        # End the stage metrics collection
                        stagemetrics.end()
                        # Clear the job group after the query execution
                        spark.sparkContext.setJobGroup("", "")

                        # Collect metrics and timing measurements
                        metrics = stagemetrics.aggregate_stagemetrics()
                        executorRunTime = round(metrics.get('executorRunTime') / 1000, 2)
                        executorCpuTime = round(metrics.get('executorCpuTime') / 1000, 2)
                        jvmGCTime = round(metrics.get('jvmGCTime') / 1000, 2)
                        elapsedTime = round(metrics.get('elapsedTime') / 1000, 2)
                        # Computed metric: average active tasks
                        avgActiveTasks = round(metrics.get('executorRunTime') / metrics.get('elapsedTime'), 1)

                        # print the timing measurements
                        print("Job finished")
                        print(f"...Start Time = {startime_string}")
                        print(f"...Elapsed Time = {elapsedTime} sec")
                        print(f"...Executors Run Time = {executorRunTime} sec")
                        print(f"...Executors CPU Time = {executorCpuTime} sec")
                        print(f"...Executors JVM GC Time = {jvmGCTime} sec")
                        print(f"...Average Active Tasks = {avgActiveTasks}")

                        # append the timing measurements to the list
                        runinfo = {'timestamp': startime_string, 'run_id': run_id, 'query': query, 'query_rerun_id': i}
                        instrumentation.append({**runinfo, **metrics})

        self.end_time = time.ctime()

        # 1. save the results to the object as a list
        self.test_results = instrumentation

        # 2. Convert results to a Pandas DataFrame
        results_pdf = pd.DataFrame(self.test_results)
        # Name the index column ID
        results_pdf.index.name = 'ID'
        # Add column avg_active_tasks
        results_pdf['avg_active_tasks'] = round(results_pdf['executorRunTime'] / results_pdf['elapsedTime'], 2)
        # add computed column elapsed time in seconds
        results_pdf['elapsed_time_seconds'] = round(results_pdf['elapsedTime'] / 1000, 2)
        # query start timestamp
        results_pdf['timestamp'] = pd.to_datetime(results_pdf['timestamp'])

        # save the results to the object
        self.results_pdf = results_pdf

        # 3. Compute and print summary metrics values grouped by query name
        grouped_results_pdf = (
            results_pdf.drop(
                columns=['query_rerun_id', 'run_id', 'avg_active_tasks', 'elapsed_time_seconds', 'timestamp'])
            .groupby('query', sort=False)  # Preserve the order of the queries
            .median()  # Can also use mean(), the median is less sensitive to outliers
        )
        # Add the computed values for avg_active_tasks and elapsed_time_seconds columns
        grouped_results_pdf['avg_active_tasks'] = round(grouped_results_pdf['executorRunTime'] / grouped_results_pdf['elapsedTime'], 2)
        grouped_results_pdf['elapsed_time_seconds'] = round(grouped_results_pdf['elapsedTime'] / 1000, 2)
        # save the grouped results to the object, rounded to the nearest integer, add the index back as the query column
        self.grouped_results_pdf = grouped_results_pdf.astype('int64').reset_index()

        # 4. Compute and print aggregated metrics values, cumulative over all queries
        # Columns to aggregate with sum, by exclusion
        aggregated_results_pdf = (results_pdf.drop(columns=['query_rerun_id', 'run_id', 'query', 'avg_active_tasks',
                                                            'elapsed_time_seconds', 'timestamp', 'peakExecutionMemory'])
                                  .sum())
        # Add new computed values for avg_active_tasks and elapsed_time_seconds columns
        aggregated_results_pdf['avg_active_tasks'] = round(aggregated_results_pdf['executorRunTime'] / aggregated_results_pdf['elapsedTime'], 2)
        aggregated_results_pdf['elapsed_time_seconds'] = round(aggregated_results_pdf['elapsedTime'] / 1000, 2)
        # round to the nearest integer and add column names
        aggregated_results_pdf = aggregated_results_pdf.astype('int64').reset_index()
        aggregated_results_pdf.columns = ['Metric_name', 'Value']
        # save the aggregated results to the object,
        self.aggregated_results_pdf = aggregated_results_pdf


    def print_test_results(self, output_file=None):
        """Print the test results to the specified output file (print to stdout if output_file is None or empty)"""

        if output_file is not None and output_file != "":
            with open(output_file, 'w') as csvfile, \
                open(output_file + ".metadata", 'w') as file_metadata, \
                open(output_file + ".grouped", 'w') as file_grouped, \
                open(output_file + ".aggregated", 'w') as file_aggregated:
                    # Write the results to the specified files
                    self.write_output(csvfile, file_metadata, file_grouped, file_aggregated)
        else:
            self.write_output() # print to stdout

    def write_output(self, file_csv=sys.stdout, file_metadata=sys.stdout, file_grouped=sys.stdout, file_aggregated=sys.stdout):
        """Write the test results to the specified output files (default is stdout), used by print_test_results() method"""

        test_results = self.test_results
        # 1. Print test configuration to a metadata text file (default is stdout)
        print("", file=file_metadata)
        print("****************************************************************************************", file=file_metadata)
        print("TPCDS with PySpark - workload configuration and metadata summary", file=file_metadata)
        print("****************************************************************************************", file=file_metadata)
        print("", file=file_metadata)

        print(f"Queries list = {', '.join(self.queries_to_run)}", file=file_metadata)
        print(f"Number of runs = {self.num_runs}", file=file_metadata)
        print(f"Query execution repeat times = {self.queries_repeat_times}", file=file_metadata)
        print(f"Total number of executed queries = {len(test_results)}", file=file_metadata)
        print(f"Sleep time (sec) between queries = {self.sleep_time}", file=file_metadata)
        print(f"Queries path = {self.queries_path}", file=file_metadata)
        print(f"Data path = {self.data_path}", file=file_metadata)
        print(f"Start time = {self.start_time}", file=file_metadata)
        print(f"End time = {self.end_time}", file=file_metadata)

        print("", file=file_metadata)
        spark = self.spark
        print(f"Spark version = {spark.version}", file=file_metadata)
        spark_master = spark.conf.get("spark.master")
        print(f"Spark master = {spark_master}", file=file_metadata)
        executor_memory = spark.conf.get("spark.executor.memory", "")
        print(f"Executor memory: {executor_memory}", file=file_metadata)
        executor_cores = spark.conf.get("spark.executor.cores", "")
        print(f"Executor cores: {executor_cores}", file=file_metadata)
        dynamic_allocation = spark.conf.get("spark.dynamicAllocation.enabled", "")
        print(f"Dynamic allocation: {dynamic_allocation}", file=file_metadata)
        if dynamic_allocation == "false":
            num_executors = spark.conf.get("spark.executor.instances")
            print(f"Number of executors: {num_executors}", file=file_metadata)
        elif dynamic_allocation == "true":
            num_min_executors = spark.conf.get("spark.dynamicAllocation.minExecutors", 0)
            print(f"Minimum Number of executors: {num_min_executors}", file=file_metadata)
            num_max_executors = spark.conf.get("spark.dynamicAllocation.maxExecutors")
            print(f"Maximum Number of executors: {num_max_executors}", file=file_metadata)
        cbo = spark.conf.get("spark.sql.cbo.enabled")
        print(f"Cost Based Optimization (CBO): {cbo}", file=file_metadata)
        hist = spark.conf.get("spark.sql.statistics.histogram.enabled")
        print(f"Histogram statistics: {hist}", file=file_metadata)
        print("", file=file_metadata)

        # Print the test results, consisting of a line for each query executed, with details on
        # the collected execution metrics.
        # the output is in csv format, printed to file_csv (default is stdout)
        if file_csv == sys.stdout:
            print("****************************************************************************************")
            print("Queries execution metrics")
            print("****************************************************************************************")
            print()
        self.results_pdf.to_csv(file_csv)

        # Print the grouped result to the specified file (default is stdout)
        if file_grouped == sys.stdout:
            print()
            print("****************************************************************************************")
            print("Median metrics values grouped by query")
            print("****************************************************************************************")
            print()
        self.grouped_results_pdf.to_csv(file_grouped, index=False)

        # Print the aggregated result to the specified file (default is stdout)
        # Transpose the result to have a single line with the aggregated values
        # Round off metrics to the nearest integer
        if file_aggregated == sys.stdout:
            print("\n****************************************************************************************")
            print("Aggregated metrics values summed over all executions")
            print("****************************************************************************************")
            print()
        self.aggregated_results_pdf.to_csv(file_aggregated, index=False)

    def save_with_spark(self, filename):
        """Save the test results to a file/folder using Spark Dataframe writer, use this to save to a cluster filesystem (HDFS, S3)"""
        spark = self.spark
        # Create a DataFrame from Pandas dataframe with test results and save to a csv file/folder using the DataFrame writer
        df = spark.createDataFrame(self.results_pdf)
        df.coalesce(1).write.option("header", "true").mode('overwrite').csv(filename)
        # results grouped by query
        df = spark.createDataFrame(self.grouped_results_pdf)
        df.coalesce(1).write.option("header", "true").mode('overwrite').csv(filename+".grouped")
        # aggregated results
        df = spark.createDataFrame(self.aggregated_results_pdf.reset_index())
        df.coalesce(1).write.option("header", "false").mode('overwrite').csv(filename+".aggregated")
