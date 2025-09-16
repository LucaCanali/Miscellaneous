# PyLatencyMap — Latency Heat Maps Visualizer
[![PyPI](https://img.shields.io/pypi/v/PyLatencyMap.svg)](https://pypi.org/project/PyLatencyMap/)

**This is a copy of the original repository for PyLatencyMap v1.3, see the home page of the project at [https://github.com/LucaCanali/PyLatencyMap](https://github.com/LucaCanali/PyLatencyMap)**


**PyLatencyMap** is a terminal-based visualizer for **latency histograms**.  
It’s intended to help with performance tuning and troubleshooting.

It renders two scrolling heat maps—**Frequency** and **Intensity**—so you can see how latency distributions evolve over time.  
Works from the command line and plays nicely with sources that output latency histograms (Oracle wait histograms,
BPF/bcc, DTrace, SystemTap, tracefiles, etc.).

---

## 📦 Installation

From PyPI:

```bash
pip install PyLatencyMap
```

Check it’s on PATH (one of):

```bash
latencymap --help
# or
python -m LatencyMap --help
```

### Alternative: clone the project

```bash
git clone https://github.com/LucaCanali/PyLatencyMap
cd PyLatencyMap
python LatencyMap.py --help
```

> Requires **Python 3.x** and a terminal that supports **ANSI colors**.

---
## 🎬 Demo video

<a href="https://www.youtube.com/watch?v=-YuShn6ro1g">
<img src="https://img.youtube.com/vi/-YuShn6ro1g/hqdefault.jpg"
      alt="Watch the demo" width="640">
</a>

---
## 🚀 Quick Start
Try PyLatencyMap with sample data

Sample data is provided in `SampleData/`. For a quick visualization:

```bash
pip install PyLatencyMap
cat SampleData/example_latency_data.txt | latencymap
```

Optionally slow down playback:

```bash
cat SampleData/example_latency_data.txt | latencymap --screen_delay=0.2
```

---

## 📚 Examples

The following assume the visualizer is installed `pip install PyLatencyMap` and available as
`latencymap` (or as `python -m LatencyMap`).

### Oracle RDBMS investigations with wait histograms (microsecond buckets)

```bash
# Oracle troubleshooting, measure I/O random reads and sample every 3 seconds
sqlplus -S system/manager@mydb \
  @Event_histograms_oracle/ora_latency_micro.sql "db file sequential read" 3 \
| latencymap

# Oracle troubleshooting, measure commit time
sqlplus -S / as sysdba \
  @Event_histograms_oracle/ora_latency_micro.sql "log file sync" 3 \
| latencymap
```

### Linux tro BPF/bcc (Linux)

```bash
# Requires bcc installed and sudo privileges
sudo bash
dnf install bcc*

python -u BPF-bcc/pylatencymap-biolatency.py -QT 3 100|python LatencyMap.py
```

### Oracle 10046 trace (microsecond buckets)

```bash
# Parse 10046 trace, filter for "db file sequential read" waits
cat SampleData/test_10046_tracefile.trc|python 10046_trace_oracle/10046_connector.py |python LatencyMap.py
```

### SystemTap (Linux block I/O)

```bash
# Requires compatible kernel, debuginfo, and stap privileges
# Install SystemTap and prepare the system on Fedora/RHEL:
sudo bash
dnf install -y systemtap systemtap-runtime
stap-prep

stap -v SystemTap/blockio_rq_issue_pylatencymap.stp 3 | python LatencyMap.py

# Example with recorded data
cat SampleData/test_SystemTap_data.txt|python SystemTap/systemtap_connector.py|python LatencyMap.py
```

### DTrace
```bash
# example with a DTrace script measuring pread latency
dtrace -s DTrace/pread_latency.d |python DTrace/dtrace_connector.py |python LatencyMap.py
```

> PyLatencyMap is **pipe-friendly**: a data source emits records, you may pass them through an optional connector to adapt the format, and finally pipe to the visualizer:

```bash
data_source | [optional_connector] | latencymap [options]
# or
data_source | [optional_connector] | python -m LatencyMap [options]
```
---

## 🧠 Why two heat maps?

Rendering latency **histograms over time** is a 3D problem (latency × time × magnitude). Heat maps make it tractable—but you need **two projections**:

1) **Frequency heat map** — *How often* events land in each bucket (events/sec).
2) **Intensity heat map** — *How much time* those events consume (ms/sec or unit/sec).

A system might show a bright band < 1 ms in **Frequency** (most ops are fast) while a thin, hotter band around 8–20 ms in **Intensity** reveals a tail that dominates end-to-end time. Both views matter.

---

## 📥 Input Format (record-oriented)

PyLatencyMap reads **tagged records** from `stdin`. Each record is delimited by `<begin record>` / `<end record>` and contains metadata plus **cumulative counts per bucket** (the tool computes deltas between records).

```
<begin record>
timestamp,microsec,<epoch_usecs>,<human_readable_ts>
latencyunit,<millisec|microsec|nanosec>
label,<free text>
datasource,<|bpf|systemtap|dtrace|oracle>
<power_of_two_value>,<cumulative_count>
<power_of_two_value>,<cumulative_count>
...
<end record>
```

**Conventions**

- `latencyunit` declares the unit used by **bucket values**; the Y-axis labels are always shown in **milliseconds**.
- Buckets must be **powers of two** (e.g., `1, 2, 4, 8, …, 2^N` in the declared unit).
- Counts are **cumulative** within each bucket; PyLatencyMap computes per-interval deltas → rates.
- `datasource` influences how **Intensity** is approximated from counts:
    - `oracle`: ~ `0.75 * bucket_value * waits`
    - `bpf  / systemtap` / `dtrace`: ~ `1.5 * bucket_value * waits`
- See `SampleData/example_latency_data.txt` for a concrete example.

---

## 🔧 Command-line Options

```text
--num_records=INT       Number of time intervals (columns). Default: 90
--min_bucket=INT        Lower bucket exponent (log2). -1 = autotune (default)
--max_bucket=INT        Upper bucket exponent (log2). 64 = autotune (default)
--frequency_maxval=F    Fix the color scale max for frequency; -1 = auto (default)
--intensity_maxval=F    Fix the color scale max for intensity; -1 = auto (default)
--screen_delay=FLOAT    Delay (s) between screens; useful for replays. Default: 0.1
--debug_level=INT       0..5 (verbosity/diagnostics). Default: 0
```

**Notes**

- Bucket “exponents” are base-2 exponents of the bucket’s upper bound in the **declared unit** (see Input Format).
- With `microsec` inputs (common), autotune sets `min_bucket = 7` (i.e., **128 µs**) and a compact vertical range.
- Fixing `*_maxval` is useful to make colors comparable across runs.

---

## 🧭 Reading the Canvas

- **Axes**
    - **X** = time, **newest at the right** (the chart fills on the right edge and scrolls left).
    - **Y** = latency buckets in **milliseconds**:
        - sub-ms rows: `.512, .256, …`; bottom row is `<.128`
        - ≥ 1 ms rows: `1, 2, 4, 8, …` (no leading dot)
- **Top map** (**Frequency**) = events/sec per bucket.
- **Bottom map** (**Intensity**) = time waited per sec (shown as `(<unit>/sec)`; labels are still in **ms**).

**Patterns to watch**

- **Two stable bands** → bimodal storage (e.g., cache vs. disk)
- **Thin hot streak at high ms** → tail outliers dominate; check saturation/retries/throttling
- **Upward drift in both maps** → generalized contention; correlate with system/DB metrics

---

## 🧪 Record & Replay

PyLatencyMap works live, but you can also record input to a file and replay it later (slower, with `--screen_delay`).
You can record a live feed to a file using Linux's `tee` for later analysis or playback:

```bash
# Record
data_source | tee /tmp/latency_feed.txt | optional_connector | latencymap

# Replay later (slower)
cat /tmp/latency_feed.txt | optional_connector | latencymap --screen_delay=0.2
```

---

## 🛠️ Tips & Troubleshooting

- **Empty or all-white map**: ensure your data stream contains *changing* cumulative counts and valid `<begin/end record>` tags.
- **Units look off**: confirm `latencyunit` is correct (`millisec|microsec|nanosec`).
- **Too few/too many rows**: override bucket range with `--min_bucket` / `--max_bucket`.
- **Colors don’t show**: use a terminal with ANSI color support; avoid piping through pagers that strip escapes.
- **Normalization across runs**: pin the color scales with `--frequency_maxval` and `--intensity_maxval`.

---

## 📂 Repository Layout (if you cloned)

```
LatencyMap.py            # Main visualizer (this tool)
SampleData/              # Example recorded inputs
SystemTap/, BPF-bcc/, DTrace/
Event_histograms_oracle/, AWR_oracle/, 10046_trace_oracle/
NetApp_Cmode/
Example*.sh              # Turnkey scripts per source
tnsnames.ora             # Helper for Oracle examples
pyproject.toml           # Packaging metadata
LICENSE                  # Project license
dist/                    # Built artifacts (when present)
```

---

## 📌 Versions

- **v1.3.0** (September 2025) — Minor refactor and testing with Python, BPF, and Oracle versions
- **v1.2.x** (2014–2016) — stability updates and examples expansion
- **v1.0** (September 2013) — initial release

---

## 👤 Author & Contact

**Luca Canali** — CERN  
📧 Luca.Canali@cern.ch  
🌐 https://cern.ch/canali

---

## 📖 References

- Blog posts:
    - Blog: [Troubleshoot I/O & Wait Latency with OraLatencyMap and PyLatencyMap](https://db-blog.web.cern.ch/node/199)
    - http://externaltable.blogspot.com/2013/08/pylatencymap-performance-tool-to-drill.html
    - http://externaltable.blogspot.com/2013/09/getting-started-with-pylatencymap.html
    - http://externaltable.blogspot.com/2015/03/heat-map-visualization-for-systemtap.html
    - http://externaltable.blogspot.com/2015/07/heat-map-visualization-of-latency.html
- Related project: **OraLatencyMap** — https://github.com/LucaCanali/OraLatencyMap
- Inspiration: Brendan Gregg, *Visualizing System Latency* and heat-map tooling

---

## 📄 License

See **LICENSE** in the repository.
