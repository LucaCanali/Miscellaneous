#!/usr/bin/env python3

import argparse
from concurrent import futures
import sys
import statistics
import time

usage = """
test_CPU_parallel.py - A basic CPU workload generator.
Luca.Canali@cern.ch - April 2023
Use this to generate CPU-intensive load on a system, running multiple threads in parallel.
The tool runs a CPU-burning loop concurrently on the system, with configurable parallelism.
The tool outputs a measurement of the CPU-burning loop execution time as a function of load.
Example:
./test_CPU_parallel.py --num_workers 2

Parameters:

--full - Full mode will test all the values of num_workers from 1 to the value 
         set with --num_workers, use this to collect speedup test measurements and create plots, default = False
--output - Optional output file, applies only to the full mode, default = None
--num_workers - Number of parallel threads running concurrently, default = 2
--num_job_execution_loops - number of times the execution loop is run on each worker, default = 3
--worker_inner_loop_size - internal weight of the inner execution loop, default = 100000000
  
"""

class test_CPU_parallel:
    """test_CPU_parallel is a basic CPU workload generator."""

    def __init__(self, num_workers, num_job_execution_loops, worker_inner_loop_size, output_csv_file):
        self.max_num_workers = num_workers
        self.num_job_execution_loops = num_job_execution_loops
        self.worker_inner_loop_size = worker_inner_loop_size
        self.output_csv_file = output_csv_file

    def cpu_intensive_inner_loop(self, n):
        """Inner loop to run a CPU-intensive task and measure the elapsed time.
        The loop size is configurable using the input parameter n.
        This is one possible implementation, you can experiment customizing this."""
        start_time = time.time()
        sum_of_squares = 0
        for i in range(1, n):
            for j in range(1, 100000):
                sum_of_squares += j * j // i
        end_time = time.time()
        return end_time - start_time

    def test_one_load(self, threads = None):
        """Run the CPU-intensive workload concurrently using future. 
           The number of concurrent worker threads is configurable.
           The number of executions is configured with self.num_executions."""
        if threads is None:
            load = self.max_num_workers
        else:
            load = threads
        timing = [] # list to store the job timing measurements
        start_time_global  = time.time()

        for i in range(self.num_job_execution_loops):
            print(f"Scheduling job batch number {i+1}")
            time.sleep(1) # short sleep before each batch
            with futures.ProcessPoolExecutor(max_workers=load + 2) as executor:
                to_do: list[futures.Future] = []
                for _ in range(load):
                    # submit jobs as futures
                    future = executor.submit(self.cpu_intensive_inner_loop, self.worker_inner_loop_size)
                    to_do.append(future)
                print(f"Scheduled running of {load} concurrent worker threads")
                # wait for futures to finish and collect the results
                for future in futures.as_completed(to_do):
                    delta_time: int = future.result()
                    print(f"{future} finished. Result, delta_time = {round(delta_time,2)} sec")
                    timing.append(delta_time)

        delta_time_global = time.time() - start_time_global
        print(f"\nCPU-intensive jobs using num_workers={load} finished, delta_time global"
              f" = {round(delta_time_global, 2)} sec")
        print("Job runtime statistics:")
        print(f"Mean job runtime = {round(statistics.mean(timing), 2)} sec")
        print(f"Median job runtime = {round(statistics.median(timing), 2)} sec")
        print(f"Standard deviation = {round(statistics.stdev(timing), 2)} sec")
        print("")
        return statistics.median(timing), statistics.mean(timing), statistics.stdev(timing)

    def print_test_results_full_mode(self, test_results, file=sys.stdout):
        """Print the test results in a CSV format, one line per test result."""
        print("Num_concurrent_jobs,job_median_run_time (sec),job_mean_run_time (sec),job_stdev_run_time (sec)",
              file=file)
        for val in test_results:
            print(f"{val.get('num_workers')},{round(val.get('job_median_timing'), 2)},"
                  f"{round(val.get('job_mean_timing'), 2)},{round(val.get('job_stdev_timing'), 2)}",
                  file=file)
        print("", file=file)

    def test_full(self):
        """Run the CPU-intensive workload with an increasing number of parallel threads
        from 1 to num_workers. Each run is executed num_job_execution_loops times."""
        print(f"Starting a full test, scanning concurrent worker thread from num_workers = 1 to {self.max_num_workers}")
        test_results = []
        for load in range(1, self.max_num_workers + 1):
            job_median_timing, job_mean_timing, job_stdev_timing = self.test_one_load(load)
            test_results.append({'num_workers':load, 'job_median_timing':job_median_timing,
                                 'job_mean_timing':job_mean_timing, 'job_stdev_timing':job_stdev_timing})

        print("\nTest results of the CPU-intensive workload generator using full mode")
        self.print_test_results_full_mode(test_results)
        if self.output_csv_file is not None:
            with open(self.output_csv_file, 'w') as csvfile:
                self.print_test_results_full_mode(test_results, csvfile)

# parse command line arguments and run the test
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Basic CPU workload generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=usage)
    parser.add_argument("--full", "-f", required=False, default=False, action='store_true',
                        help="full mode will test all the values of num_workers from 1 to the value in --num_workers, "
                             "use this data collection mechanism as input for create performance analysis and plots")
    parser.add_argument("--num_workers", "-w", action = 'store', type = int,  required=False, help="Number of workers", default=2)
    parser.add_argument("--output_file", "-o", action = 'store', required=False, help="Optional output file, applies only to full-mode", default=None)
    parser.add_argument("--num_job_execution_loops", action = 'store', type = int,  required=False, help="Number of job execution loops", default=3)
    parser.add_argument("--worker_inner_loop_size", action = 'store', type = int,  required=False, help="Worker operation loop size", default=3000)
    args = parser.parse_args()
    test = test_CPU_parallel(args.num_workers,
                             args.num_job_execution_loops,
                             args.worker_inner_loop_size,
                             args.output_file)
    if args.full:
        test.test_full()
    else:    
        test.test_one_load()
