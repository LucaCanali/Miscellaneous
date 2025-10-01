# Notes on converting from ROOT format

## 1. PySpark Python datasource for ROOT

The [PySpark Python datasource for ROOT](https://github.com/cerndb/pyspark-root-datasource) runs on Spark 4 and
allows to read ROOT files into Spark dataframes.

Example:
```
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

More details and examples at the project home page: [PySpark Python datasource for ROOT](https://github.com/cerndb/pyspark-root-datasource) 


## 2. Laurelin

Laurelin is an implementation of a Spark Datasource V2 written in Java.  
Note: Laurelin 1.6.0 with Spark 3.x, requires Java 8 (Java 11 and Java 17 do not appear to work with that version). Example:  

```
export JAVA_HOME=<path to java 8 home>

spark-shell .... \
--conf spark.executorEnv.JAVA_HOME=$JAVA_HOME --conf spark.yarn.appMasterEnv.JAVA_HOME=$JAVA_HOME
```

Apache Spark with the [Laurelin library](https://github.com/spark-root/laurelin)
can be used to ingest file in ROOT format and convert them Apache Parquet or Apache ORC, among others.  

The following example uses spark-shell to run the conversion, it can be run, with minor changes,
with PySpark too. 

`spark-shell --master local[*] --packages edu.vanderbilt.accre:laurelin:1.6.0 --driver-memory 8g`

The input is a file in ROOT format, download it from CERN opendata. For example:
[Run2012BC_DoubleMuParked_Muons.root](https://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root)

`val df=spark.read.format("root").option("tree", "Events").load("<path>/Run2012BC_DoubleMuParked_Muons.root")`

---
## Note

When converting small files, it can be useful to compact (coalesce) the output to 1 file before writing:  
`df.coalesce(1).write.parquet("<path>/Run2012BC_DoubleMuParked_Muons.parquet")`

For large files:  

```
val df = spark.read.parquet("CMSOpenDataDimuon_large.parquet")
df.coalesce(64).write.parquet("CMSOpenDataDimuon_large_compacted.parquet")
```

