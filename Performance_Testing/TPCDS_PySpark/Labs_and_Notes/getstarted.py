#!/usr/bin/env python
#
# Get started with TPCDS_PySpark
#
# Requierements:
# pip install tpcds_pyspark
# pip install pyspark
# pip install sparkmeasure
# pip install pandas
#
# Download the test data
# wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/TPCDS/tpcds_10.zip
# unzip -q tpcds_10.zip

from tpcds_pyspark import TPCDS

# Create an instance of TPCDS
# Run a minimal test
tpcds = TPCDS(num_runs=1, queries_repeat_times=1, queries=['q1','q2'])

# Use this to run a full test
# tpcds = TPCDS()

tpcds.map_tables()
tpcds.run_TPCDS()

tpcds.print_test_results()
