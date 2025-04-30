# test_cpu_parallel – CPU & Memory Load Generator in Rust

[![crate](https://img.shields.io/crates/v/test_cpu_parallel.svg)](https://crates.io/crates/test_cpu_parallel)
[![docs.rs](https://docs.rs/test_cpu_parallel/badge.svg)](https://docs.rs/test_cpu_parallel)

`test_cpu_parallel` is a **small, zero‑dependency load‑testing kit**.  It can:

* load cores to verify scaling or system/container limits
* sweep 1 → *N* threads and export a tidy CSV for speed‑up plots
* hammer the memory hierarchy with random‑access touches beyond the LLC
* run **stand‑alone** from the CLI *or* be **embedded** in your own Rust code

A two‑minute build, no external data files, works on Linux, macOS and Windows.

Link to the [Project page](https://github.com/LucaCanali/Miscellaneous/tree/master/Performance_Testing/Test_CPU_parallel_Rust)

---
## 📦 Installation

| what you want                | command |
|------------------------------|---------|
| **CLI binary** (optimised)   | `cargo install test_cpu_parallel` |
| **Library** in an app / lib  | `cargo add test_cpu_parallel` |
| **Dev build from source**    | `git clone … && cargo build` |

> **Note** For benchmark *accuracy* the CLI defaults to an **un‑optimised** `opt‑level = 0` build.  If you install with `cargo install` a `--release` build is produced; results will differ slightly.  Re‑compile locally with `cargo build` to reproduce blog numbers.

---
## ⚡ CLI quick‑start

```bash
# Burn four threads for a few seconds
$ test_cpu_parallel -w 4

# Sweep 1 → 16 threads, write CSV
$ test_cpu_parallel --num_workers 16 --full -o results.csv

# Stress memory with 8 workers and a 512 MiB buffer
$ test_cpu_parallel -w 8 --mode memory --memory_size 512
```

Run `test_cpu_parallel --help` for the complete flag list (excerpt below).

```text
Usage: test_cpu_parallel [OPTIONS]
  -w, --num_workers <N>        parallel threads      (default 2)
  -m, --mode <cpu|memory>      workload type         (default cpu)
  -f, --full                   sweep 1‥=N threads
  -o, --output_file <PATH>     write CSV (full mode)
      --memory_size <MiB>      buffer for memory test (default 1024)
```

---
## 📚 Library usage

Embed the engine in unit tests, benchmarks or monitoring agents:

```rust
use test_cpu_parallel::TestCPUParallel;

fn main() -> anyhow::Result<()> {
    // 4 workers, one batch, memory workload, 64 MiB buffer
    let bench = TestCPUParallel::new(4, 1, 1_000, "", 64);
    let (thread_stats, batch_stats) = bench.test_one_load(None, "memory")?;
    println!("Per‑thread  stats: {thread_stats:?}");
    println!("Per‑batch   stats: {batch_stats:?}");
    Ok(())
}
```

API docs are hosted on **[docs.rs/test_cpu_parallel](https://docs.rs/test_cpu_parallel)**.

---
## 🔧 Building from source

```bash
# Clone and build a debug binary (recommended for comparable timings)
$ git clone https://github.com/LucaCanali/Miscellaneous.git
$ cd Miscellaneous/Performance_Testing/Test_CPU_parallel_Rust
$ cargo build            # ≈ 35 s on a modern laptop
```

* Tested on Rust **1.74+** – that is the MSRV.
* Setting `cargo build --release` enables heavy optimisations and changes loop timing; avoid if you care about exact comparability.

---
## 📊 Analysing the CSV

Full‑mode output is a single CSV line per thread count, ready to feed into
Python/pandas, gnuplot or Excel.  See the `Notebooks/` directory in the repo for ready‑made Jupyter notebooks that plot speed‑up and efficiency curves.

---
## More

* Project page & extended docs – <https://github.com/LucaCanali/Miscellaneous/tree/master/Performance_Testing/Test_CPU_parallel_Rust>
* Blog article that motivated the tool – <https://db-blog.web.cern.ch/node/189>
* Licence – **Apache‑2.0**

Enjoy hacking your CPUs 🔥

