#!/bin/bash

# This is an example launcher script for PyLatencyMap 
# Collect and display SystemTap data for the block I/O request calls as a Frequency-Intensity Latency HeatMap
# This can be used to investigate single-block read latency 
# Note this scripts requires to have SystemTap installed 

stap -v SystemTap/blockio_rq_issue_pylatencymap.stp 3 |python SystemTap/systemtap_connector.py |python LatencyMap.py

#
# when using Systemtap v2.6 or higher you can use this instead
# stap -v SystemTap/blockio_rq_issue_pylatencymap_new.stp 3 |python SystemTap/systemtap_connector.py |python LatencyMap.py
#
