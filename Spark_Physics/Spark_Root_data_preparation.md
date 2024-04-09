## Notes on converting from ROOT format

Apache Spark with the [Laurelin library](https://github.com/spark-root/laurelin)
can be used to ingest file in ROOT format and convert them Apache Parquet or Apache ORC, among others.  

The following example uses spark-shell to run the conversion, it can be run, with minor changes,
with PySpark too. 

`spark-shell --master local[*] --packages edu.vanderbilt.accre:laurelin:1.6.0 --driver-memory 8g`

The input is a file in ROOT format, download it from CERN opendata. For example:
[Run2012BC_DoubleMuParked_Muons.root](https://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root)

`val df=spark.read.format("root").option("tree", "Events").load("<path>/Run2012BC_DoubleMuParked_Muons.root")`

For small files, compact (coalesce) the output to 1 file before writing:  
`df.coalesce(1).write.parquet("<path>/Run2012BC_DoubleMuParked_Muons.parquet")`

For large files:  

```
val df = spark.read.parquet("CMSOpenDataDimuon_large.parquet")
df.coalesce(64).write.parquet("CMSOpenDataDimuon_large_compacted.parquet")
```

---
Note, when using Laurelin 1.6.0, use Java 8 (not Java 11). Example:  

```
export JAVA_HOME=<path to java 8 home>

spark-shell .... \
--conf spark.executorEnv.JAVA_HOME=$JAVA_HOME --conf spark.yarn.appMasterEnv.JAVA_HOME=$JAVA_HOME
```