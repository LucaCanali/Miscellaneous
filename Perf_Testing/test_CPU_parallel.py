#!/usr/bin/env python3

import argparse
from concurrent import futures
import statistics
import time

examples = """
Basic CPU workload generator.
Use this to generate CPU-intensive load on a system in parallel.
The tool runs a CPU-burning loop concurrently on the system with a configurable load.
The tool provides measurements of the CPU-burning loop as function of load.
Example:
./test_CPU_parallel.py -w 2

Parameters:
--full - full mode will test all the values of num_workers from 1 to the value in --num_workers, use this to create plots, default = False
--num_workers - Number of parallel threads running concurrently, default = 2
--num_job_execution_loops - number of times the execution loop is run on each worker, default = 2
--worker_inner_loop_size - internal weight of the inner execution loop, default = 100000000
"""

def calculate_sum_squares(n):
    start_time = time.time()
    sum_of_squares = 0
    for i in range(n):
        sum_of_squares += i**2
    end_time = time.time()
    return end_time - start_time

def test_one_load(num_workers, num_job_execution_loops, worker_inner_loop_size):
    num_executions = num_workers * num_job_execution_loops
    start_time_global  = time.time()
    with futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        to_do: list[futures.Future] = []
    
        # submit table import jobs as futures
        for i in range(num_executions):
            future = executor.submit(calculate_sum_squares, worker_inner_loop_size)
            to_do.append(future)
        print(f"Scheduled running of {num_executions} jobs using num_workers = {num_workers}")
        
        # wait for futures to finish and collect the results
        timing = []
        for future in futures.as_completed(to_do):
            delta_time: int = future.result()
            print(f"{future} finished. Result, delta_time = {round(delta_time,2)} sec")
            timing.append(delta_time)
    delta_time_global = time.time() - start_time_global  
    print(f"Scheduled running of {num_executions} jobs using num_workers={num_workers} finished, delta_time global = {round(delta_time_global, 2)} sec")
    print(f"Job runtime statistics. Mean job runtime = {round(statistics.mean(timing),2)} sec. Median job runtime = {round(statistics.median(timing),2)} sec")
    return(statistics.median(timing))

def test_full(num_workers, num_job_execution_loops, worker_inner_loop_size):
    print("Starting a full test, scannig from num_workers = 1 to {num_workers}")
    test_results = []
    for i in range(1, num_workers + 1):
        job_median_timing = test_one_load(i, num_job_execution_loops, worker_inner_loop_size)
        test_results.append({'num_workers':i, 'job_median_timing':job_median_timing})
        print()
    print("CPU workload test generator test results")
    print("Num_concurrent_jobs, job_median_run_time (sec)")
    for val in test_results:
        print(f"{val.get('num_workers')}, {round(val.get('job_median_timing'),2)}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Basic CPU workload generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples)
    parser.add_argument("--full", "-f", required=False, default=False, action='store_true',
                        help="full mode will test all the values of num_workers from 1 to the value in --num_workers, use this to create plots")
    parser.add_argument("--num_workers", "-w", action = 'store', type = int,  required=False, help="Number of workers", default=2)
    parser.add_argument("--num_job_execution_loops", "-i", action = 'store', type = int,  required=False, help="Number of job execution loops", default=2)
    parser.add_argument("--worker_inner_loop_size", "-n", action = 'store', type = int,  required=False, help="Worker operation loop size", default=100000000)
    args = parser.parse_args()
    num_workers = args.num_workers
    num_job_execution_loops = args.num_job_execution_loops
    worker_inner_loop_size= args.worker_inner_loop_size
    full = args.full
    if full:
        test_full(num_workers, num_job_execution_loops, worker_inner_loop_size)
    else:    
        test_one_load(num_workers, num_job_execution_loops, worker_inner_loop_size)

