# PySpark Datasource for ROOT


**The development repository for PySpark ROOT Data Source is at [pyspark-root-datasource](https://github.com/cerndb/pyspark-root-datasource)**   
Apache Spark 4 Python Datasource for reading files in the **ROOT** data format used in High-Energy Physics (HEP).

**Author and version**  
Luca.Canali@cern.ch · v0.1 (Sep 2025)

## Highlights

- ✅ Allows to read ROOT data using Apache Spark using a custom Spark 4 Python DataSource.
- ✅ Works with local files, directories, and globs; optional **XRootD** (`root://`) support.
- ✅ Implements partitioning and optional schema inference.
- ✅ Powered by [**Uproot**](https://github.com/scikit-hep/uproot5), [**Awkward Array**](https://github.com/scikit-hep/awkward), [**PyArrow**](https://arrow.apache.org/) and [Spark's Python Datasource](https://spark.apache.org/docs/latest/api/python/tutorial/sql/python_data_source.html#python-data-source-reader-with-direct-arrow-batch-support-for-improved-performance).
- Blog: [Why I’m Loving Spark 4’s Python Data Source (with Direct Arrow Batches)](https://db-blog.web.cern.ch/node/200)

---
## Install

```bash
# From PyPI
pip install pyspark-root-datasource

# Or, local for development
pip install -e .
```

---

## Quick start

```python
from pyspark.sql import SparkSession
from pyspark_root_datasource import register

spark = (SparkSession.builder
         .appName("Read ROOT via PySpark + uproot")
         .getOrCreate())

# Register the datasource (short name = "root")
register(spark)

# Get the example ROOT file (2 GB)
# xrdcp root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root .
# if you don't have xrdcp installed, on Linux use wget or curl -O
wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012BC_DoubleMuParked_Muons.root

# Best practice: provide a schema to prune branches early
schema = "nMuon int, Muon_pt array<float>, Muon_eta array<float>, Muon_phi array<float>, Muon_mass array<float>, Muon_charge array<int>"

df = (spark.read.format("root")
      .schema(schema)
      .option("path", "/data/Run2012BC_DoubleMuParked_Muons.root")
      .option("tree", "Events")
      .option("step_size", "1000000")
      .load())

df.show(5, truncate=False)
print("Count:", df.count())

# Use schema inference
df2 = (spark.read.format("root")
       .option("path", "/data/Run2012BC_DoubleMuParked_Muons.root")
       .option("tree", "Events")
       .option("sample_rows", "1000")   # default 1000
       .load())
df2.printSchema()
```

---
## Examples and tests

- Read ROOT using PySpark: [read_root_file.py](examples/read_root_file.py)
- Run tests using with `pytest`
- Example notebook, showing how to make a plot from ROOT files: 
  - [Dimuon_mass_spectrum.ipynb](examples/Dimuon_mass_spectrum.ipynb)

---
## Options

- `"path"` **(required)** – file path, URL, comma-separated list, directory, or glob (e.g. `"/data/*.root"`)
- `"tree"` (default: `"Events"`) – TTree name
- `"step_size"` (default: `"1000000"`) – entries per **Spark partition** (per file)
- `"num_partitions"` (optional, per file) – overrides `step_size`
- `"entry_start"`, `"entry_stop"` (optional, per file) – index bounds
- `"columns"` – comma-separated branch names (if not providing a Spark schema)
- `"list_to32"` (default: `"true"`) – Arrow list offset width
- `"extensionarray"` (default: `"false"`) – Arrow extension array support
- `"cast_unsigned"` (default: `"true"`) – cast `uint*` → signed (Spark lacks unsigned)
- `"recursive"` (default: `"false"`) – expand directories recursively
- `"ext"` (default: `"*.root"`) – filter pattern when `path` is a directory
- `"sample_rows"` (default: `"1000"`) – rows for schema inference
- `"arrow_max_chunksize"` (default: `"0"`) – if >0, limit rows per Arrow RecordBatch

---
## Reading over XRootD (`root://`)

```bash
# fsspec plugins for xrootd
pip install fsspec fsspec-xrootd

# XRootD client libs + Python bindings
conda install -c conda-forge xrootd
```

Install the extras, then:

```python
remote_file = "root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root"
df = (spark.read.format("root")
      .option("path", remote_file)
      .option("tree", "Events")
      .load())
df.show(3, truncate=False)
```

---

## Reading folders, globs, recursion

```python
# All .root files in a directory (non-recursive)
df = (spark.read.format("root")
      .option("path", "/data/myfolder")
      .load())

# Recursive directory expansion
df = (spark.read.format("root")
      .option("path", "/data/myfolder")
      .option("recursive", "true")
      .load())

# Custom extension used when 'path' is a directory
df = (spark.read.format("root")
      .option("path", "/data/myfolder")
      .option("ext", "*.parquet.root")
      .load())

# Glob
df = (spark.read.format("root")
      .option("path", "/data/*/atlas/*.root")
      .load())
```

---
## Tips and troubleshooting

- Prefer **explicit schemas** to prune early and minimize I/O.  
- Tune **partitioning**:  
  - `step_size` = entries per Spark partition.  
  - `num_partitions` (per file) overrides `step_size`.  
- Large jagged arrays benefit from reasonable `step_size` (e.g., `100k–1M`).  
- If necessary, use `arrow_max_chunksize` to keep batch sizes moderate for downstream stages.  
- `cast_unsigned=true` normalizes `uint*` to signed widths (Spark-friendly).  
- Fixed-size lists are preserved as Arrow `fixed_size_list` (no silent downgrade).
- **XRootD errors**: install both `fsspec` and `fsspec-xrootd`, and the XRootD client libs. Conda is often the smoothest:  
  ```bash
  pip install fsspec fsspec-xrootd
  conda install -c conda-forge xrootd
  ```
- **Tree not found**: double-check `.option("tree", "...")`; error messages list available keys.  
- **Different schemas across files**: ensure compatible branch types or read by subsets, then reconcile in Spark.  
- **Driver vs executors env mismatch**: set both `spark.pyspark.python` and `spark.pyspark.driver.python` to your Python.

---
## Related work & acknowledgments

- **ROOT format** — part of the [ROOT project](https://root.cern/).
- **Core SciKit-HEP dependencies** — [uproot](https://github.com/scikit-hep/uproot5) and [awkward](https://github.com/scikit-hep/awkward) (thanks to Jim Pivarski).
- **Spark Python data sources**
  - Docs: [Python Data Source API](https://spark.apache.org/docs/latest/api/python/tutorial/sql/python_data_source.html)
  - Curated list: [awesome-python-datasources](https://github.com/allisonwang-db/awesome-python-datasources) (thanks to Allison Wang)
  - Example: [Datasource for Hugging Face datasets](https://github.com/huggingface/pyspark_huggingface)
- **Arrow batch support** — [SPARK-48493](https://issues.apache.org/jira/browse/SPARK-48493) (thanks to Allison Wang) adds direct Arrow RecordBatch ingestion for higher throughput.
- **Examples & notes**
  - Notebooks: [Apache Spark for Physics](https://github.com/LucaCanali/Miscellaneous/tree/master/Spark_Physics)
  - Guide: [Reading ROOT files with Spark](https://github.com/LucaCanali/Miscellaneous/blob/master/Spark_Physics/Spark_Root_data_preparation.md)
  - Blog: [Why I’m Loving Spark 4’s Python Data Source (with Direct Arrow Batches)](https://db-blog.web.cern.ch/node/200)

### Notes & limitations

- **Performance** — Python data sources cross the Python↔JVM boundary, which adds overhead. Using [Direct Arrow Batch support](https://spark.apache.org/docs/latest/api/python/tutorial/sql/python_data_source.html#python-data-source-reader-with-direct-arrow-batch-support-for-improved-performance) substantially reduces serialization cost and improves throughput. For maximum performance, a native JVM **DataSource V2** implementation typically wins (see the guide on [reading ROOT with Spark](https://github.com/LucaCanali/Miscellaneous/blob/master/Spark_Physics/Spark_Root_data_preparation.md)).
- **Scope** — This datasource is **read-only** at this stage.

