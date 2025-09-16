#!/bin/bash

# This is an example launcher script for PyLatencyMap
# Replays SystemTap trace data for ,easured block I/O latency as a Frequency-Intensity Latency HeatMap

cat SampleData/test_SystemTap_data.txt |python SystemTap/systemtap_connector.py |python LatencyMap.py

