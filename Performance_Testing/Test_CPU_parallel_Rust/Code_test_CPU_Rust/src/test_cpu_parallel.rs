use rayon::prelude::*;
use std::time::Instant;
use std::io::Write;
use std::fs::File;
use std::path::Path;
use std::hint::black_box;
use statrs::statistics::{Data, Median, Distribution};

pub struct TestCPUParallel {
    max_num_workers: usize,
    num_job_execution_loops: usize,
    worker_inner_loop_size: usize,
    output_csv_file: String,
}

impl TestCPUParallel {
    pub fn new(max_num_workers: usize, num_job_execution_loops: usize, worker_inner_loop_size: usize,
           output_csv_file: String) -> Self {
        TestCPUParallel {
            max_num_workers,
            num_job_execution_loops,
            worker_inner_loop_size,
            output_csv_file,
        }
    }

    fn cpu_intensive_inner_loop(&self, n: usize) -> f64 {
        let start_time = Instant::now();
        let mut val: usize = 0;
        for i in 1..n {
            for j in 1..100000 {
                val += j * j / i;
            }
        }
        // black_box is used to prevent the compiler from optimizing away the loop
        black_box(val);
        let end_time = Instant::now();
        let duration = end_time.duration_since(start_time);
        duration.as_secs_f64()
    }

    pub fn test_one_load(&self, threads: Option<usize>) -> (f64, f64, f64) {
        let load = threads.unwrap_or(self.max_num_workers);
        let mut timings = Vec::new();

        for i in 0..self.num_job_execution_loops {
            println!("Scheduling job batch number {}", i+1);
            // short sleep before each batch
            std::thread::sleep(std::time::Duration::from_secs(1));

            let pool = rayon::ThreadPoolBuilder::new()
                .num_threads(load)
                .build()
                .unwrap();

            let results: Vec<_> = pool.install(|| {
                (0..load).into_par_iter().map(|_| self.cpu_intensive_inner_loop(self.worker_inner_loop_size)).collect()
            });

            println!("Scheduled running of {} concurrent worker threads", load);

            for (idx, delta_time) in results.into_iter().enumerate() {
                println!("Job {} finished. Result, delta_time = {:.2} sec", idx, delta_time);
                timings.push(delta_time);
            }
        }

        println!("\nCPU-intensive jobs using num_workers={} finished.", load);

        let measurements = Data::new(timings);
        let median_job_runtime = measurements.median();
        let mean_job_runtime = measurements.mean().unwrap();
        let stdev_job_runtime= measurements.std_dev().unwrap();

        println!("Job runtime statistics:");
        println!("Mean job runtime = {:.2} sec", mean_job_runtime);
        println!("Median job runtime = {:.2} sec", median_job_runtime);
        println!("Standard deviation = {:.2} sec", stdev_job_runtime);
        println!("");

        (median_job_runtime, mean_job_runtime, stdev_job_runtime)
    }

    fn print_test_results_full_mode(&self, test_results: &Vec<(usize, f64, f64, f64)>) {
        println!("Num_concurrent_jobs,job_median_run_time (sec),job_mean_run_time (sec),job_stdev_run_time (sec)");

        for (num_workers, median_time, mean_time, stdev_time) in test_results {
            println!("{},{:.2},{:.2},{:.2}", num_workers, median_time, mean_time, stdev_time);
        }

        println!();

        if &self.output_csv_file != "" {
            let path = Path::new(&self.output_csv_file );
            let mut file = File::create(&path).unwrap();

            writeln!(file, "Num_concurrent_jobs,job_median_run_time (sec),job_mean_run_time (sec),job_stdev_run_time (sec)").unwrap();
            for (num_workers, median_time, mean_time, stdev_time) in test_results {
                writeln!(file, "{},{:.2},{:.2},{:.2}", num_workers, median_time, mean_time, stdev_time).unwrap();
            }

            writeln!(file).unwrap();
        }
    }

    pub fn test_full(&self) {
        println!("Starting a full test, scanning concurrent worker thread from num_workers = 1 to {}", self.max_num_workers);

        let mut test_results = Vec::new();

        for load in 1..=self.max_num_workers {
            let (job_median_timing, job_mean_timing, job_stdev_timing) = self.test_one_load(Some(load));
            test_results.push((load, job_median_timing, job_mean_timing, job_stdev_timing));
        }

        println!("\nTest results of the CPU-intensive workload generator using full mode");
        self.print_test_results_full_mode(&test_results);
    }
}
