use rayon::prelude::*;
use std::time::Instant;
use std::io::{BufWriter, Write};
use std::fs::File;
use std::path::Path;
use statrs::statistics::{Data, Median, Distribution};

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
    memory_size: usize,
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
        output_csv_file: String,
        memory_size: usize,
    ) -> Self {
        Self {
            max_num_workers,
            num_job_execution_loops,
            worker_inner_loop_size,
            output_csv_file: if output_csv_file.is_empty() {
                None
            } else {
                Some(output_csv_file)
            },
            memory_size,
        }
    }

    /// Memory-plus-CPU workload: random touches beyond L2 size.
    pub fn memory_cpu_intensive_inner_loop(&self, iterations: usize) -> f64 {
        // Convert MiB → bytes and round to next power-of-two so we can mask.
        let size_bytes = (self.memory_size * 1024 * 1024).next_power_of_two();
        let mut array: Vec<usize> = vec![0; size_bytes / 8];
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
                touch!(); touch!(); touch!(); touch!();
                touch!(); touch!(); touch!(); touch!();
            }
        }

        std::hint::black_box(&array);
        start.elapsed().as_secs_f64()
    }

    /// Pure CPU-heavy loop.
    fn cpu_intensive_inner_loop(&self, iterations: usize) -> f64 {
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

    /// Run one load and return *thread* **and** *batch* statistics.
    pub fn test_one_load(&self, threads: Option<usize>, mode: &str)
        -> Result<((f64, f64, f64), (f64, f64, f64)), String>
    {
        let load = threads.unwrap_or(self.max_num_workers);
        let mut thread_times = Vec::with_capacity(self.num_job_execution_loops * load);
        let mut batch_times  = Vec::with_capacity(self.num_job_execution_loops);
        const BATCH_DELAY: std::time::Duration = std::time::Duration::from_millis(500);

        println!(
            "Starting test with {load} worker threads for {} batches (mode: {mode}).",
            self.num_job_execution_loops
        );

        let inner_loop: Box<dyn Fn(usize) -> f64 + Send + Sync> = match mode {
            "cpu"    => Box::new(|it| self.cpu_intensive_inner_loop(it)),
            "memory" => Box::new(|it| self.memory_cpu_intensive_inner_loop(it)),
            _ => return Err(format!("Invalid mode '{mode}'. Use 'cpu' or 'memory'.")),
        };

        for batch_idx in 0..self.num_job_execution_loops {
            println!("Running batch {}/{} with {} threads", batch_idx + 1, self.num_job_execution_loops, load);
            std::thread::sleep(BATCH_DELAY);

            let batch_start = Instant::now();

            let pool = rayon::ThreadPoolBuilder::new()
                .num_threads(load)
                .build()
                .map_err(|e| format!("Failed to build thread pool: {e}"))?;

            let results: Vec<f64> = pool.install(|| {
                (0..load).into_par_iter()
                          .map(|worker_id| {
                              let t = inner_loop(self.worker_inner_loop_size);
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

        // ----- statistics -----
        let thread_stats = Data::new(thread_times);
        let batch_stats  = Data::new(batch_times);

        let t = (
            thread_stats.median(),
            thread_stats.mean().unwrap_or_default(),
            thread_stats.std_dev().unwrap_or_default(),
        );
        let b = (
            batch_stats.median(),
            batch_stats.mean().unwrap_or_default(),
            batch_stats.std_dev().unwrap_or_default(),
        );

        println!(
            "Statistics → Threads  median {0:.2}s, mean {1:.2}s, stdev {2:.2}s\nStatistics → Batches  median {3:.2}s, mean {4:.2}s, stdev {5:.2}s",
            t.0, t.1, t.2, b.0, b.1, b.2
        );

        Ok((t, b))
    }

    /// Sweep 1‥=max_num_workers and print both thread- and batch-level summaries.
    pub fn test_full(&self, mode: &str) -> Result<(), String> {
        println!(
            "Starting full test, threads 1→{} (mode: {}).", self.max_num_workers, mode
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
            "Threads", "Thread-Median", "Thread-Mean", "Thread-Std", "Batch-Median", "Batch-Mean", "Batch-Std"
        );
        println!("{}", "-".repeat(88));
        for (w, t_med, t_mean, t_std, b_med, b_mean, b_std) in r {
            println!(
                "{:<10} {:<12.2} {:<12.2} {:<12.2} {:<12.2} {:<12.2} {:<12.2}",
                w, t_med, t_mean, t_std, b_med, b_mean, b_std
            );
        }
    }

    fn write_results_to_csv(&self, r: &[(usize, f64, f64, f64, f64, f64, f64)]) -> Result<(), String> {
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
        ).map_err(|e| format!("Failed to write header: {e}"))?;

        for (w, t_med, t_mean, t_std, b_med, b_mean, b_std) in r {
            writeln!(
                writer,
                "{},{:.2},{:.2},{:.2},{:.2},{:.2},{:.2}",
                w, t_med, t_mean, t_std, b_med, b_mean, b_std
            ).map_err(|e| format!("Failed to write row: {e}"))?;
        }

        println!("Results → '{}'", path.display());
        Ok(())
    }
}
