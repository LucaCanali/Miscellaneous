#!/bin/bash

# This is an example launcher script for PyLatencyMap 
# The sqlplus script outputs data from v$event_histogram for the Disk file I/O Calibration read wait event
# Use this when measuring workload from calibrate_io 
# LatencyMap.py diplays data as two heatmaps: a Frequency-Intensity and a Latency HeatMap
# This script is intended to be used to measure the latency drilldown for calibrate_io workload 
#
# The example here below is added for convenience. It shows how to run calibrate_io workload from sql*plus
# 
#SET SERVEROUTPUT ON
#DECLARE
#  lat  INTEGER;
#  iops INTEGER;
#  mbps INTEGER;
#BEGIN
#   DBMS_RESOURCE_MANAGER.CALIBRATE_IO (10, 10, iops, mbps, lat);
#
#  DBMS_OUTPUT.PUT_LINE ('max_iops = ' || iops);
#  DBMS_OUTPUT.PUT_LINE ('latency  = ' || lat);
#  DBMS_OUTPUT.PUT_LINE ('max_mbps = ' || mbps);
#end;
#/
#
#

sqlplus -S / as sysdba @Event_histograms_oracle/ora_latency.sql "Disk file I/O Calibration" 3 | python LatencyMap.py

