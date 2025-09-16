#!/bin/bash

# This is an example launcher script for PyLatencyMap 
# Display Oracle's event histogram historical data from AWR as a Frequency-Intensity Latency HeatMap
# This example is for db file sequential read: can be used to study AWR data for random read latency and IOPS
#

sqlplus -S / as sysdba @AWR_oracle/awr_latency.sql "db file sequential read" 91 | python LatencyMap.py


