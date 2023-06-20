#!/usr/bin/env python3

import argparse
from pyspark.sql import SparkSession, DataFrame
import sys
from sparkmeasure import StageMetrics
import time

usage = """
test_Spark_CPU_memory.py - A workload generator with Apache Spark, instrumented using sparkMeasure.
Luca.Canali@cern.ch - April 2023
Use this to generate CPU-intensive and memory-intensive load on a system.
The tool runs a PySpark job with concurrent activity by multiple tasks,
with configurable load.
Multiple runs are performed and the average execution time is reported.
The tool outputs measurements of the job execution time as a function of load,
as well as metrics from sparkMeasure, notably executor tasks run time, 
CPU time and Garbage collection time.
Use full mode to collect speedup measurements and create plots.
Example:
./test_Spark_CPU_memory.py --num_workers 2

Parameters:

--full - Full mode will test all the values of num_workers from 1 to the value 
         set with --num_workers, use this to collect speedup test measurements and create plots, default = False
--output - Optional output file, applies only to the full mode, default = None
--num_workers - Number of parallel threads running concurrently, default = 2
--num_job_execution_loops - number of times the execution loop is run on each worker, default = 3
--worker_inner_loop_size - internal weight of the inner execution loop, default = 100000000
--spark_heap_size - Spark heap size, default = 64g
--data_path - path to the parquet files used for testing, default = ./store_sales.parquet
--sparkmeasure_path - path to the sparkmeasure package, default = ./spark-measure_2.12-0.23.jar
"""

class test_Spark_CPU_memory:
    """test_Spark_CPU_memory_sparkmeasure is a load generator, using Apache Spark and mostly
    stressing CPU and memory access. It is further instrumented using sparkMeasure.
    """

    def __init__(self, num_workers, num_job_execution_loops, spark_heap_size,
                 output_csv_file, data_path, sparkmeasure_path):
        self.max_num_workers = num_workers
        self.num_job_execution_loops = num_job_execution_loops
        self.spark_heap_size = spark_heap_size
        self.output_csv_file = output_csv_file
        self.data_path = data_path
        self.sparkmeasure_path = sparkmeasure_path

    def test_one_load(self, tasks = None):
        """Run the CPU-intensive workload concurrently using Spark.
           The number of concurrent tasks is configurable.
           The number of job runs is configured with self.num_executions."""
        if tasks is None:
            load = self.max_num_workers
        else:
            load = tasks
        heap_mem = self.spark_heap_size
        timing = [] # list to store the job timing measurements
        # allocate the Spark session, use local mode with the desired number of concurrent tasks
        print(f"Allocating a Spark session in local mode with {load} concurrent tasks")
        print(f"Heap memory size = {heap_mem}, data_path = {self.data_path}")
        print(f"sparkmeasure_path = {self.sparkmeasure_path}")
        spark = (SparkSession.builder
                 .appName("Test Spark_CPU_memory")
                 .master(f"local[{load}]")
                 .config("spark.driver.memory", heap_mem)
                 .config("spark.driver.extraJavaOptions", "-XX:+UseG1GC") # G1GC to handle large heap size
                 .config("spark.sql.parquet.filterPushdown", "false")
                 .config("spark.jars", self.sparkmeasure_path)
                 .getOrCreate()
                 )
        df= spark.read.parquet(self.data_path)
        # debug
        # df= spark.read.parquet("./store_sales.parquet/part-00000-2fabb079-b0ed-4e32-ba2b-382048dd60a0-c000.snappy.parquet")
        stagemetrics = StageMetrics(spark)
        for i in range(self.num_job_execution_loops):
            print(f"Scheduling job number {i+1}")
            time.sleep(1) # short sleep before each job run
            stagemetrics.begin()
            start_time = time.time()
            df.filter("ss_sales_price=-1").collect()
            end_time = time.time()
            stagemetrics.end()
            delta_time = round(end_time - start_time,2)
            metrics = stagemetrics.aggregate_stagemetrics()
            executorRunTime = round(metrics.get('executorRunTime')/1000,2)
            executorCpuTime = round(metrics.get('executorCpuTime')/1000,2)
            jvmGCTime = round(metrics.get('jvmGCTime')/1000,2)
            print(f"Job finished, job_run_time (elapsed time) = {round(delta_time,2)} sec")
            print(f"...executors Run Time = {executorRunTime} sec")
            print(f"...executors CPU Time = {executorCpuTime} sec")
            print(f"...executors jvmGC Time = {jvmGCTime} sec")
            timing.append({'num_workers':load, 'job_run_time':delta_time, 'executorRunTime':executorRunTime,
                          'executorCpuTime':executorCpuTime, 'jvmGCTime':jvmGCTime})
        spark.stop()
        return timing

    def print_test_results_full_mode(self, test_results, file=sys.stdout):
        print("Num_concurrent_tasks,run_number,job_run_time (sec),executorRunTime (sec),executorCpuTime (sec),jvmGCTime (sec)",
              file=file)
        for test in test_results:
            for i,val in enumerate(test): # enumerate the list of dictionaries
                print(f"{val.get('num_workers')},{i+1},{val.get('job_run_time')},"
                    f"{val.get('executorRunTime')},{val.get('executorCpuTime')},{val.get('jvmGCTime')}",
                    file=file)
        print("", file=file)

    def test_full(self):
        """Run the CPU-intensive workload with an increasing number of parallel threads
        from 1 to num_workers. Each run is executed num_job_execution_loops times."""
        print(f"Starting a full test, scanning concurrent worker thread from num_workers = 1 to {self.max_num_workers}")
        test_results = []
        for load in range(1, self.max_num_workers + 1):
            test_results.append(self.test_one_load(load)) # run the workload and collect timing and metrics

        print("\nTest results of the CPU-intensive workload generator using full mode")
        self.print_test_results_full_mode(test_results)
        if self.output_csv_file is not None:
            with open(self.output_csv_file, 'w') as csvfile:
                self.print_test_results_full_mode(test_results, csvfile)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="test_Spark_CPU_memory_sparkmeasure is a load generator implemented on to of Apache Spark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=usage)
    parser.add_argument("--full", "-f", required=False, default=False, action='store_true',
                        help="full mode will test all the values of num_workers from 1 to the value in --num_workers, "
                             "use this data collection mechanism as input for create performance analysis and plots")
    parser.add_argument("--num_workers", "-w", action = 'store', type = int,  required=False, help="Number of workers", default=8)
    parser.add_argument("--spark_heap_size", action = 'store', required=False, help="Spark heap size", default="64g")
    parser.add_argument("--output_file", "-o", action = 'store', required=False, help="Optional output file, applies only to full mode", default=None)
    parser.add_argument("--num_job_execution_loops", action = 'store', type = int, required=False, help="Number of job execution loops", default=3)
    parser.add_argument("--data_path", action = 'store', required=False, help="path to the parquet files used for testing", default="./store_sales.parquet")
    parser.add_argument("--sparkmeasure_path", action = 'store', required=False, help="path to the sparkmeasure jar", default="./spark-measure_2.12-0.23.jar")

    args = parser.parse_args()
    test = test_Spark_CPU_memory(args.num_workers, args.num_job_execution_loops, args.spark_heap_size,
                                 args.output_file, args.data_path, args.sparkmeasure_path)
    if args.full:
        test.test_full()
    else:    
        test.test_one_load()
