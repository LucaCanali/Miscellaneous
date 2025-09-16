#!/usr/bin/python

# dtrace_connector.py
# this is part of the PyLatencyMap package, Luca.Canali@cern.ch Aug 2013
# Input: dtrace data in PyLatencyMap format, for example from pread_tracedata.d script 
# Output: histogram record data in a format to be processes by LatencyMap.py for 
#         visualization as Frequency-Intensity HeatMap
#
# Usage:
#        dtrace -s DTrace/pread_tracedata.d |python DTrace/dtrace_connector.py
#

import sys

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            print('\nReached EOF from data source, exiting.')
            sys.exit(0)
        if line.strip() == '':
            continue
        line = line.strip()

        if line.startswith('<begin record>'):
            print('<begin record>')
            continue
        if line.startswith('<end record>'):
            print('<end record>')
            sys.stdout.flush()
            continue
        if line.startswith('timestamp'):
            print(line)
            continue
        if line.startswith('label'):
            print(line)
            continue
        if 'value' in line:
            continue
        if 'myhistogram' in line:
            continue

        line = line.replace(' ','')
        line = line.replace('@','')
        line = line.replace('|',',')

        if line.startswith('-'):
            continue             # filters out point of negative latency, this is a workaround 
        print(line)              # when using DTrace on Virtualbox 

if __name__ == '__main__':
    sys.exit(main())





