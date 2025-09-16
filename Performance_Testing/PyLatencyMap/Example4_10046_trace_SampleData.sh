#!/bin/bash

# This is an example launcher script for PyLatencyMap 
# Display 10046 trace data as a Frequency-Intensity Latency HeatMap
# This example is for db file sequential read: can be used to study random-read time latency
# The data source is a trace file (cat from an example trace file here)
# When using this in a real case you can also use tail -f of the tracefile as the source for
# near real-time latency visualization.
# Reminder on how to activate 10046 trace for an oracle session:
# exec dbms_monitor.session_trace_enable(<sid>, <serial#>)
#

cat SampleData/test_10046_tracefile.trc|python 10046_trace_oracle/10046_connector.py |python LatencyMap.py 

