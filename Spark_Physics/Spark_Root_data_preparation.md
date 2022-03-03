## Notes on converting from ROOT format

Apache Spark with the Laurelin library (https://github.com/spark-root/laurelin)
can be used to ingest file in ROOT format and convert them Apache Parquet and Apache ORC.  

The following example uses spark-shell to run the conversion, it can be run, with minor changes, with PySpark too.  
Laurelin 1.1.1 does not work with Spark 3.x, we use Spark 2.4.8 for this:  

`bin/spark-shell --master local[*] --packages edu.vanderbilt.accre:laurelin:1.1.1 --driver-memory 8g`

The input is a file in ROOT format, download it from CERN opendata. For example:
https://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root

`val df=spark.read.format("root").option("tree", "Events").load("/home/luca/DoubleMuParked/Run2012BC_DoubleMuParked_Muons.root")`

// For small files, compact (coalesce) the output to 1 file before writing:
`df.coalesce(1).write.mode("overwrite").parquet("/home/luca/DoubleMuParked/Run2012BC_DoubleMuParked_Muons.parquet")`

// For large files:
// First write with full parallelism
// then read back in and compact (coalesce) into a smaller number of files as in:

val df = spark.read.parquet("CMSOpenDataDimuon_large.parquet")
df.coalesce(64).write.parquet("CMSOpenDataDimuon_large_compacted.parquet")
