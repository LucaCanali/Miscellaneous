use rayon::prelude::*;
use std::time::Instant;
use std::io::{BufWriter, Write};
use std::fs::File;
use std::path::Path;
use statrs::statistics::{Data, Median, Distribution};
use rand::Rng;

/// Represents the configuration and functionality for CPU or memory-intensive tests.
///
/// This struct manages the parameters for running parallel workload tests and
/// provides methods for executing and analyzing these tests.
pub struct TestCPUParallel {
    /// Maximum number of worker threads to use.
    max_num_workers: usize,

    /// Number of times the execution loop is run on each worker thread.
    num_job_execution_loops: usize,

    /// Number of iterations in the inner loop of each worker thread.
    worker_inner_loop_size: usize,

    /// Optional output file path for writing test results as a CSV.
    output_csv_file: Option<String>,
}

impl TestCPUParallel {
    /// Creates a new instance of `TestCPUParallel`.
    ///
    /// # Arguments
    /// - `max_num_workers`: Maximum number of worker threads to use.
    /// - `num_job_execution_loops`: Number of times the execution loop is run on each worker thread.
    /// - `worker_inner_loop_size`: Number of iterations in the inner loop of each worker thread.
    /// - `output_csv_file`: Path to the CSV output file for saving results. If empty, no file will be written.
    ///
    /// # Returns
    /// A new instance of `TestCPUParallel`.
    pub fn new(
        max_num_workers: usize,
        num_job_execution_loops: usize,
        worker_inner_loop_size: usize,
        output_csv_file: String,
    ) -> Self {
        TestCPUParallel {
            max_num_workers,
            num_job_execution_loops,
            worker_inner_loop_size,
            output_csv_file: if output_csv_file.is_empty() {
                None
            } else {
                Some(output_csv_file)
            },
        }
    }

    /// Performs a Memory- and CPU-intensive computation with randomized memory access
    /// to simulate a workload that stresses both CPU and memory bandwidth.
    ///
    /// This function is designed to exceed the L2 cache size to force main memory
    /// access for most operations.
    ///
    /// # Arguments
    /// - `iterations`: Number of outer iterations to perform.
    ///
    /// # Returns
    /// The elapsed time in seconds as a `f64`.
    fn memory_cpu_intensive_inner_loop(&self, iterations: usize) -> f64 {
        let start_time = Instant::now(); // Start timing

        // Create a vector large enough to exceed L2 cache size
        // Each `usize` is 8 bytes on 64-bit systems, so 100M elements = 800 MB.
        let mut array: Vec<usize> = vec![0; 100_000_000];
        let mut rng = rand::thread_rng(); // Initialize random number generator
        let array_len = array.len(); // Cache the array length for efficiency

        for _ in 0..iterations {
            for _ in 0..10_000 {
                // Generate a random index and perform a computation to stress memory and CPU
                let idx = rng.gen_range(0..array_len); // Generate random index
                array[idx] = std::hint::black_box(array[idx].wrapping_add(1)); // Prevent compiler optimization
            }
        }

        // Prevent the entire array from being optimized out
        std::hint::black_box(&array);

        start_time.elapsed().as_secs_f64() // Return elapsed time
    }

    /// Performs a purely CPU-intensive computation to simulate workload.
    /// This loop focuses on mathematical operations without memory bottlenecks.
    ///
    /// # Arguments
    /// - `iterations`: Number of iterations to perform.
    ///
    /// # Returns
    /// The elapsed time in seconds as a `f64`.
    fn cpu_intensive_inner_loop(&self, iterations: usize) -> f64 {
        let start_time = Instant::now(); // Start the timer
        let mut val: usize = 0; // Accumulator for CPU computations

        for i in 1..iterations {
            for j in 1..1_000_000 {
                // Perform CPU-intensive mathematical operations.
                // The combination of multiplication, addition, and bit masking
                // ensures that the compiler cannot fully optimize this loop.
                val = std::hint::black_box(val.wrapping_add((i.wrapping_mul(j) ^ j) & 0xFF));
            }
        }

        // Prevent compiler optimizations on the final result
        std::hint::black_box(val);

        start_time.elapsed().as_secs_f64() // Return elapsed time
    }

    /// Runs a single test load and returns runtime statistics.
    ///
    /// # Arguments
    /// - `threads`: Optional number of threads to use. Defaults to `self.max_num_workers` if `None`.
    /// - `mode`: Specifies which inner loop to use:
    ///   - `"cpu"` for the CPU-intensive inner loop.
    ///   - `"memory"` for the memory+CPU-intensive inner loop.
    ///
    /// # Returns
    /// A `Result` with a tuple containing median, mean, and standard deviation of execution times.
    pub fn test_one_load(&self, threads: Option<usize>, mode: &str) -> Result<(f64, f64, f64), String> {
        let load = threads.unwrap_or(self.max_num_workers);
        let mut timings = Vec::with_capacity(self.num_job_execution_loops);
        const BATCH_DELAY: std::time::Duration = std::time::Duration::from_millis(500);

        println!(
            "Starting test with {} concurrent worker threads for {} job execution loops (mode: {}).",
            load, self.num_job_execution_loops, mode
        );

        // Determine the inner loop function to use
        let inner_loop: Box<dyn Fn(usize) -> f64 + Send + Sync> = match mode {
            "cpu" => Box::new(|iterations| self.cpu_intensive_inner_loop(iterations)),
            "memory" => Box::new(|iterations| self.memory_cpu_intensive_inner_loop(iterations)),
            _ => return Err(format!("Invalid mode '{}'. Use 'cpu' or 'memory'.", mode)),
        };

        for i in 0..self.num_job_execution_loops {
            println!("Running batch {}/{}", i + 1, self.num_job_execution_loops);
            // Introduce a short delay between test batches to reduce resource contention
            std::thread::sleep(BATCH_DELAY);

            let pool = rayon::ThreadPoolBuilder::new()
                .num_threads(load)
                .build()
                .map_err(|e| format!("Failed to build thread pool: {}", e))?;

            let results: Vec<_> = pool.install(|| {
                (0..load)
                    .into_par_iter()
                    .map(|worker_id| {
                        // Execute the chosen inner loop
                        let timing = inner_loop(self.worker_inner_loop_size);
                        println!(
                            "Job {} finished (mode: {}). Result, delta_time = {:.2} sec",
                            worker_id, mode, timing
                        );
                        timing // Return the timing for collection
                    })
                    .collect()
            });

            println!("Completed batch {}/{}.", i + 1, self.num_job_execution_loops);
            timings.extend(results);
        }

        let measurements = Data::new(timings.clone());
        let median = measurements.median();
        let mean = measurements.mean().unwrap_or_default();
        let stdev = measurements.std_dev().unwrap_or_default();

        println!(
            "Test completed for {} threads (mode: {}). Mean: {:.2}s, Median: {:.2}s, StdDev: {:.2}s",
            load, mode, mean, median, stdev
        );

        Ok((median, mean, stdev))
    }

    /// Runs tests for all thread loads from 1 to `max_num_workers`.
    ///
    /// This method iterates through a range of thread counts (from 1 to `max_num_workers`)
    /// and executes the workload using the specified `mode` for each configuration.
    /// Results are printed to the console and optionally written to a CSV file.
    ///
    /// # Arguments
    /// - `mode`: Specifies the type of workload to execute:
    ///   - `"cpu"`: Runs a CPU-intensive workload.
    ///   - `"memory"`: Runs a memory-intensive workload.
    ///
    /// # Returns
    /// A `Result` indicating success or failure.
    /// - On success: Returns `Ok(())`.
    /// - On failure: Returns an error message as `Err(String)`.
    pub fn test_full(&self, mode: &str) -> Result<(), String> {
        println!(
            "Starting full test with worker threads ranging from 1 to {} (mode: {}).",
            self.max_num_workers, mode
        );

        // Vector to store results for each configuration of worker threads.
        // Each entry will store the number of threads and the statistics (median, mean, std_dev).
        let mut results = Vec::with_capacity(self.max_num_workers);

        // Iterate through thread counts from 1 to `max_num_workers`.
        for workers in 1..=self.max_num_workers {
            println!("Testing with {} worker threads...", workers);

            // Perform the workload test for the current number of threads and mode.
            // Calls `test_one_load` to execute the workload and gather runtime statistics.
            let (median, mean, stdev) = self.test_one_load(Some(workers), mode)?;

            // Append the results (number of threads and statistics) to the results vector.
            results.push((workers, median, mean, stdev));
        }

        // Once all tests are completed, print a summary of the results.
        println!("Full test completed. Summary:");
        self.print_test_results(&results);

        // Optionally write the results to a CSV file if an output file is specified.
        // This method handles file creation, writing, and error handling.
        self.write_results_to_csv(&results)
    }

    /// Prints test results to the console in a formatted table.
    ///
    /// # Arguments
    /// - `results`: A slice of tuples where each tuple contains:
    ///   - `usize`: The number of worker threads.
    ///   - `f64`: Median runtime in seconds.
    ///   - `f64`: Mean runtime in seconds.
    ///   - `f64`: Standard deviation of runtime in seconds.
    fn print_test_results(&self, results: &[(usize, f64, f64, f64)]) {
        // Print the header with clear column labels
        println!("{:<12} {:<20} {:<20} {:<20}",
            "Num Threads", "Median Runtime (s)", "Mean Runtime (s)", "StdDev Runtime (s)");
        println!("{}", "-".repeat(72)); // Add a horizontal separator for readability

        // Print each row of results with aligned columns
        for (workers, median, mean, stdev) in results {
            println!("{:<12} {:<20.2} {:<20.2} {:<20.2}", workers, median, mean, stdev);
        }

        println!("\nTest results printed successfully.");
    }

    /// Writes test results to a CSV file if an output file is specified.
    ///
    /// # Arguments
    /// - `results`: A slice of tuples where each tuple contains:
    ///   - `usize`: Number of threads.
    ///   - `f64`: Median runtime in seconds.
    ///   - `f64`: Mean runtime in seconds.
    ///   - `f64`: Standard deviation of runtime in seconds.
    ///
    /// # Returns
    /// A `Result` indicating success or failure:
    /// - On success: Returns `Ok(())`.
    /// - On failure: Returns an error message as `Err(String)`.
    fn write_results_to_csv(&self, results: &[(usize, f64, f64, f64)]) -> Result<(), String> {
        // Check if an output file is specified; if not, exit early.
        let output_file = match &self.output_csv_file {
            Some(file) => file, // Unwrap the file path if present
            None => {
                println!("No output file specified. Skipping CSV export.");
                return Ok(());
            }
        };

        // Define the file path for the CSV output.
        let path = Path::new(output_file);

        // Attempt to create the file and wrap it in a buffered writer.
        let file = File::create(path).map_err(|e| {
            format!(
                "Failed to create CSV file '{}': {}",
                path.display(),
                e
            )
        })?;
        let mut writer = BufWriter::new(file);

        // Write the header row to the CSV file.
        writeln!(
            writer,
            "Num_Threads,Median_Runtime,Mean_Runtime,StdDev_Runtime"
        )
        .map_err(|e| format!("Failed to write header to CSV file '{}': {}", path.display(), e))?;

        // Write each result row to the CSV file.
        for (threads, median, mean, stdev) in results {
            writeln!(writer, "{},{:.2},{:.2},{:.2}", threads, median, mean, stdev).map_err(|e| {
                format!(
                    "Failed to write data row to CSV file '{}': {}",
                    path.display(),
                    e
                )
            })?;
        }

        // Print confirmation of successful CSV export.
        println!("Results successfully written to '{}'", path.display());
        Ok(())
    }

}
