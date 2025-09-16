#!/bin/bash

# This is an example launcher script for PyLatencyMap 
# The sqlplus script outputs data from gv$event_histogram_micro for the wait event log file sync
# LatencyMap.py displays data as Frequency-Intensity heatmaps
# This script is intended to be used to perform latency drilldown of the commit time wait event
# 

sqlplus -S / as sysdba @Event_histograms_oracle/ora_latency_micro.sql "log file sync" 3 | python LatencyMap.py

