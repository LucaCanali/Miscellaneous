#!/bin/bash

# This is an example launcher script for PyLatencyMap 
# Replays DTrace trace data for the pread and pread64 system calls as a Frequency-Intensity Latency HeatMap
# Note: Original data taken with DTrace on a test machine
# (see also http://externaltable.blogspot.com/2013/06/dtrace-explorations-of-oracle-wait.html)

cat SampleData/test_DTrace_data.txt | python DTrace/dtrace_connector.py| python LatencyMap.py

