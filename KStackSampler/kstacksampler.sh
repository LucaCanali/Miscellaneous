#!/bin/bash
#
# kstacksampler.sh - poor man's profiler for kernel stack trace profiling for Linux
#
# This script is intended to be used together with flame graphs https://github.com/brendangregg/FlameGraph
# What it does: it reads from /proc/pid/stack at regular intervals and prints the output to stdout      
# Use it to investigate processes that are spending most of their time off CPU and/or in system calls.
#
# Notes: 
#  - this is a basic script, consider it as a proof of concept/study material.
#  - the overhead on the measured system is expected to be low when used with care.
#  - for CPU-bound processes use rather perf for stack profiling and On-CPU flame graph techniques.
#  - the use of shell for profiling does not allow for high frequency
#  - stacks are captured "in flight" using the /proc filesystem this minimizes the risk but also reduces accuracy
#  - stack values and process state are read in two different calls, they may not match if the process state changes
#  - the script traces one process (although it could be adapted to trace multiple pids)
#  - the script does not trace threads (although it can be modified to trace tids from /proc/pid/task/tid/stack)
#  - the script does not provide userspace traces
#  - processes state "running" refers to both running and runnable (in run queue)  
#                  
# Example of usage together with Flamegraphs: 
# ./kstacksampler.sh -p 1234 -n 10 -i .05 | grep -v 0xffffffffffffffff | sed 's/State:\t//g'| sed 's/\[<.*>] //g' | \
# ../FlameGraph/stackcollapse-stap.pl | ../FlameGraph/flamegraph.pl
#
# Author Luca.Canali@cern.ch
# First release, October 2015
#
# See also this blog post:
# http://externaltable.blogspot.com/2015/10/linux-kernel-stack-profiling-and-flame.html
#
# Additional credits and ideas who have inspired this: 
# Brendan Gregg ->
#   http://www.brendangregg.com/FlameGraphs/offcpuflamegraphs.html
# Tanel Poder   -> 
#   http://blog.tanelpoder.com/2013/02/21/peeking-into-linux-kernel-land-using-proc-filesystem-for-quickndirty-troubleshooting/
#

iterations=50
interval=0.1

function usage {
   cat <<-END >&2
      USAGE: offcpu -p pid -n iterations -i interval
               -p pid        # process id to trace, mandatory parameter
               -n iterations # number of stack traces to collect, default $iterations
               -i interval   # sleep interval in seconds between stack traces, default $interval
END
exit
}

while getopts :p:n:i:h opt
do
   case $opt in
	p)	pid=$OPTARG ;;
	n)	iterations=$OPTARG ;;
	i)	interval=$OPTARG ;;
        h|?) usage ;;
    esac
done

if !(($pid)); then
   usage
   exit
fi


if [ ! -d "/proc/$pid" ]; then
   echo "ERROR: pid=$pid does not exist or you don't have permissions to read /proc/$pid" >&2
   exit 
fi

for x in $(seq 1 $iterations); do
   cat /proc/$pid/stack         # get kernel stack trace from /proc
             # this is an approximation as the process state may have changed to runnable in the meantime
   grep -m 1 State /proc/$pid/status
   echo "1"  # this makes the output ingestable by FlameGraph-master/stackcollapse-stap.pl
   echo ""
   sleep $interval
done 

