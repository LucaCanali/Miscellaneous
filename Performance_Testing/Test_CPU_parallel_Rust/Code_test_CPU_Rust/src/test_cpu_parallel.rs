use rayon::prelude::*;
use statrs::statistics::{Data, Median, Statistics};
use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::Path;
use std::time::{Duration, Instant};

/// Workload type to run.
#[derive(Copy, Clone, Debug)]
pub enum WorkloadMode {
    Cpu,
    Memory,
}

/// Represents the configuration and functionality for CPU- or memory-intensive tests.
pub struct TestCPUParallel {
    /// Maximum number of worker threads the benchmark will try.
    max_num_workers: usize,

    /// How many batches each worker executes.
    num_job_execution_loops: usize,

    /// Inner-loop iterations per worker.
    worker_inner_loop_size: usize,

    /// Optional CSV output path.
    output_csv_file: Option<String>,

    /// Size *in MiB* of the buffer used by the memory workload.
    memory_size_mib: usize,
}

/// Very small xorshift RNG: 3 shifts + 2 xors = one “random” `u64`.
#[inline(always)]
fn xorshift64(state: &mut u64) -> u64 {
    let mut x = *state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    *state = x;
    x
}

impl TestCPUParallel {
    /// Create a new benchmark harness.
    pub fn new(
        max_num_workers: usize,
        num_job_execution_loops: usize,
        worker_inner_loop_size: usize,
        output_csv_file: Option<String>,
        memory_size_mib: usize,
    ) -> Self {
        Self {
            max_num_workers,
            num_job_execution_loops,
            worker_inner_loop_size,
            output_csv_file,
            memory_size_mib,
        }
    }

    /// Memory-plus-CPU workload: random touches beyond L2 size.
    ///
    /// Returns elapsed time in seconds.
    pub fn memory_cpu_intensive_inner_loop(&self, iterations: usize) -> f64 {
        // Convert MiB → bytes and round to next power-of-two so we can mask.
        let size_bytes = (self.memory_size_mib * 1024 * 1024).next_power_of_two();
        let mut array: Vec<usize> = vec![0; size_bytes / std::mem::size_of::<usize>()];
        let len_mask = array.len() - 1;
        let mut rng_state = 0x0055_aa55_f00d_f00d_u64; // non-zero seed

        let start = Instant::now();

        const TOUCHES_PER_ITER: usize = 50_000;
        const UNROLL: usize = 8;
        let passes = TOUCHES_PER_ITER / UNROLL;

        for _ in 0..iterations {
            for _ in 0..passes {
                macro_rules! touch {
                    () => {{
                        let idx = (xorshift64(&mut rng_state) as usize) & len_mask;
                        // SAFETY: idx < array.len() because we mask with len_mask
                        unsafe {
                            *array.get_unchecked_mut(idx) =
                                array.get_unchecked(idx).wrapping_add(1);
                        }
                    }};
                }
                touch!();
                touch!();
                touch!();
                touch!();
                touch!();
                touch!();
                touch!();
                touch!();
            }
        }

        std::hint::black_box(&array);
        start.elapsed().as_secs_f64()
    }

    /// Pure CPU-heavy loop.
    ///
    /// Returns elapsed time in seconds.
    pub fn cpu_intensive_inner_loop(&self, iterations: usize) -> f64 {
        let start = Instant::now();
        let mut val: usize = 0;

        for i in 0..iterations {
            for j in 1..1_000_000 {
                val = std::hint::black_box(val.wrapping_add((i.wrapping_mul(j) ^ j) & 0xFF));
            }
        }

        std::hint::black_box(val);
        start.elapsed().as_secs_f64()
    }

 
    fn summarize(samples: Vec<f64>) -> (f64, f64, f64) {
        if samples.is_empty() {
            return (0.0, 0.0, 0.0);
        }

        // Median via `Data` + `Median` trait
        let data = Data::new(samples.clone());
        let median = data.median();

        // Mean and std dev via slice + `Statistics` trait
        let slice = samples.as_slice();
        let mean = slice.mean();
        let std_dev = slice.std_dev();

        (median, mean, std_dev)
    }

    /// Run one load and return *thread* **and** *batch* statistics.
    pub fn test_one_load(
        &self,
        threads: Option<usize>,
        mode: WorkloadMode,
    ) -> Result<((f64, f64, f64), (f64, f64, f64)), String> {
        let load = threads.unwrap_or(self.max_num_workers);
        let mut thread_times = Vec::with_capacity(self.num_job_execution_loops * load);
        let mut batch_times = Vec::with_capacity(self.num_job_execution_loops);
        const BATCH_DELAY: Duration = Duration::from_millis(500);

        println!(
            "Starting test with {load} worker threads for {} batches (mode: {:?}).",
            self.num_job_execution_loops, mode
        );

        let pool = rayon::ThreadPoolBuilder::new()
            .num_threads(load)
            .build()
            .map_err(|e| format!("Failed to build thread pool: {e}"))?;

        for batch_idx in 0..self.num_job_execution_loops {
            println!(
                "Running batch {}/{} with {} threads",
                batch_idx + 1,
                self.num_job_execution_loops,
                load
            );
            std::thread::sleep(BATCH_DELAY);

            let batch_start = Instant::now();

            let results: Vec<f64> = pool.install(|| {
                (0..load)
                    .into_par_iter()
                    .map(|worker_id| {
                        let t = match mode {
                            WorkloadMode::Cpu => {
                                self.cpu_intensive_inner_loop(self.worker_inner_loop_size)
                            }
                            WorkloadMode::Memory => {
                                self.memory_cpu_intensive_inner_loop(self.worker_inner_loop_size)
                            }
                        };
                        println!("Thread {worker_id} finished, Δt = {t:.2}s");
                        t
                    })
                    .collect()
            });

            let batch_elapsed = batch_start.elapsed().as_secs_f64();
            println!("Batch elapsed time: {batch_elapsed:.2}s\n");

            thread_times.extend(results);
            batch_times.push(batch_elapsed);
        }

        let thread_stats = Self::summarize(thread_times);
        let batch_stats = Self::summarize(batch_times);

        println!(
            "Statistics → Threads  median {0:.2}s, mean {1:.2}s, stdev {2:.2}s\n\
             Statistics → Batches  median {3:.2}s, mean {4:.2}s, stdev {5:.2}s",
            thread_stats.0,
            thread_stats.1,
            thread_stats.2,
            batch_stats.0,
            batch_stats.1,
            batch_stats.2
        );

        Ok((thread_stats, batch_stats))
    }

    /// Sweep 1‥=max_num_workers and print both thread- and batch-level summaries.
    pub fn test_full(&self, mode: WorkloadMode) -> Result<(), String> {
        println!(
            "Starting full test, threads 1→{} (mode: {:?}).",
            self.max_num_workers, mode
        );

        // (threads, t_med, t_mean, t_std, b_med, b_mean, b_std)
        let mut results = Vec::with_capacity(self.max_num_workers);

        for workers in 1..=self.max_num_workers {
            println!("\n===== Workers: {workers} =====");
            let ((t_med, t_mean, t_std), (b_med, b_mean, b_std)) =
                self.test_one_load(Some(workers), mode)?;
            results.push((workers, t_med, t_mean, t_std, b_med, b_mean, b_std));
        }

        println!("\nFull test completed. Summary:\n");
        self.print_test_results(&results);
        self.write_results_to_csv(&results)
    }

    fn print_test_results(&self, r: &[(usize, f64, f64, f64, f64, f64, f64)]) {
        println!(
            "{:<10} {:<12} {:<12} {:<12} {:<12} {:<12} {:<12}",
            "Threads",
            "Thread-Median",
            "Thread-Mean",
            "Thread-Std",
            "Batch-Median",
            "Batch-Mean",
            "Batch-Std"
        );
        println!("{}", "-".repeat(88));
        for (w, t_med, t_mean, t_std, b_med, b_mean, b_std) in r {
            println!(
                "{:<10} {:<12.2} {:<12.2} {:<12.2} {:<12.2} {:<12.2} {:<12.2}",
                w, t_med, t_mean, t_std, b_med, b_mean, b_std
            );
        }
    }

    fn write_results_to_csv(
        &self,
        r: &[(usize, f64, f64, f64, f64, f64, f64)],
    ) -> Result<(), String> {
        let Some(path_str) = &self.output_csv_file else {
            println!("No output file specified — skipping CSV export.");
            return Ok(());
        };

        let path = Path::new(path_str);
        let file = File::create(path)
            .map_err(|e| format!("Failed to create CSV '{}': {e}", path.display()))?;
        let mut writer = BufWriter::new(file);

        writeln!(
            writer,
            "NumThreads,ThreadMedian,ThreadMean,ThreadStd,BatchMedian,BatchMean,BatchStd"
        )
        .map_err(|e| format!("Failed to write header: {e}"))?;

        for (w, t_med, t_mean, t_std, b_med, b_mean, b_std) in r {
            writeln!(
                writer,
                "{},{:.2},{:.2},{:.2},{:.2},{:.2},{:.2}",
                w, t_med, t_mean, t_std, b_med, b_mean, b_std
            )
            .map_err(|e| format!("Failed to write row: {e}"))?;
        }

        println!("Results written to '{}'", path.display());
        Ok(())
    }
}
