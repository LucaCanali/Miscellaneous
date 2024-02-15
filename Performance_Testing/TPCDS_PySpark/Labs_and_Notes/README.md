# Labs and Notes on running TPCDS with PySpark

TPCDS is a standard benchmark for SQL-based systems. This repo contains a set of labs and notes on running TPCDS with PySpark.
The main idea is to use TPCDS as a workload generator for performance testing and optimization of Apache Spark workloads.
In particular, this is to test Spark metrics instrumentation and performance troubleshooting tools such as [sparkMeasure](https://github.com/LucaCanali/sparkMeasure)
the [Spark WebUI](https://spark.apache.org/docs/latest/web-ui.html) and the [Spark Dashboard](https://github.com/cerndb/spark-dashboard)

## Contents
- [getstarted.py](getstarted.py) is a simple example of how to run TPCDS with PySpark
- [TPCDS_PySpark_CERN_SWAN_getstarted.ipynb](TPCDS_PySpark_CERN_SWAN_getstarted.ipynb) is a Jupyter notebook with labs and notes on running TPCDS with PySpark
- [TPCDS_analysis_scale_10000G.ipynb](TPCDS_analysis_scale_10000G.ipynb) is a Jupyter notebook with labs and notes on analyzing TPCDS results at scale
- [tpcds_run_results](tpcds_run_results) is a directory with example output from running TPCDS with PySpark
- [TPCDS_schema.md](TPCDS_schema.md) contains a description of the TPCDS schema used by TPCDS_PySpark, with a list of the tables and details of their columns and data types
- [TPCDS_queries](TPCDS_queries) contains a description of selected TPCDS queries used by TPCDS_PySpark, with a list of the queries and their SQL code
