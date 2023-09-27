# Flame Graphs

Stack traces are a powerful tool for understanding the performance of your code. They can be used to identify hotspots, and to understand the impact of optimizations. 
Flame graphs are a visualization of stack traces that makes it easy to see which code paths are most common, and which are the most expensive.
There are multiple tools available to collect stack traces depending on the programming language and the operating system.  
Here a few examples of tools that can be used to collect stack traces:

1. Binary programs: use bcc-tools or perf
2. Java programs: use async-profiler
3. Python programs: use py-spy

See also:
- [Spark and Pyroscope](../Spark_Notes/Tools_Spark_Pyroscope_FlameGraph.md)
- the blog post
  [Enhancing Apache Spark Performance with Flame Graphs: A Practical Example Using Grafana Pyroscope](https://db-blog.web.cern.ch/node/193)

The following examples show how to use these tools to collect stack traces and generate flame graphs.
1. bcc-tools
   - See also https://github.com/iovisor/bcc and
     https://brendangregg.com/flamegraphs.html
   - Setup: install bcc-tools
      - `dnf install bcc-tools` (on RedHat derivatives)
   - Setup get the FlameGraphs scripts
      - `git clone https://github.com/brendangregg/FlameGraph
   - Collect the folded stack traces
      - `/usr/share/bcc/tools/profile -df -p 12073 10 > test_profile1.txt` 
   - Generate the flame graph
      - `FlameGraph/flamegraph.pl test_profile1.txt > test_profile1.svg`
- 1b. You can use perf instead of bcc-tools
   - see https://github.com/brendangregg/FlameGraph

2. Java: async-profiler
   - See also [Note on Spark and Flamegraphs](../../../Spark_Notes/Spark_and_Flamegraphs.md)
   - Setup: install async-profiler
      - Download the binary or build from https://github.com/async-profiler/async-profiler
   - Examples:
      ```
      # profile by time (regardless if process is on CPU or waiting)
      ./profiler.sh -e wall -d 30 -f $PWD/flamegraph1.html <pid_of_JVM>
              
      # profile on-CPU threads, without using perf
      ./profiler.sh -e itimer -d 30 -f $PWD/flamegraph1.html <pid_of_JVM>
     
      # profile on-CPU threads, using perf   
      ./profiler.sh -e cpu -d 30 -f $PWD/flamegraph1.html <pid_of_JVM>
     
      # list available events
      ./profiler.sh list <pid_of_JVM>
      ```
     
3. Python: py-spy
   - See also [Note on Spark and Flamegraphs](../../../Spark_Notes/Spark_and_Flamegraphs.md)
   - Example:   
   `py-spy record -d 30 -p <pid> --nonblocking -o myFlamegraph.svg`
