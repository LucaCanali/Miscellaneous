#!/bin/bash

# Example launcher for PyLatencyMap (Oracle wait-event latency drilldown).
# Prerequisite (if using the PyPI console script or module):  pip install PyLatencyMap
# - Samples gv$event_histogram_micro for "db file sequential read" (single-block random read).
# - Sampling interval = 3 seconds (change the trailing "3" to adjust).
# - Renders two terminal heat maps:
#     • Frequency = events/sec per latency bucket (IOPS-like)
#     • Intensity = time waited per sec (unit/sec; Y-axis labels shown in ms)
# Tip: if installed from PyPI, you can replace `python LatencyMap.py` with `latencymap`.
# Option: connect with credentials instead of SYSDBA (uncomment the next line and comment the active one):
# sqlplus -S system/manager@mydb @Event_histograms_oracle/ora_latency_micro.sql "db file sequential read" 3 | python LatencyMap.py
# Or, when using the console script:
# sqlplus -S system/manager@mydb @Event_histograms_oracle/ora_latency_micro.sql "db file sequential read" 3 | latencymap

sqlplus -S / as sysdba @Event_histograms_oracle/ora_latency_micro.sql "db file sequential read" 3 | python LatencyMap.py
