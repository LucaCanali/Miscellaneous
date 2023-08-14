# Linux tools for OS metrics/performance measurements

- A list of Linux tools and diagnostic utilities for OS-based investigations

- Measure CPU used by the JVM: 
  - ```$ ps -efo cputime -p <pid_Spark_JVM>```
  - Get the metrics directly from `/proc/<pid>/stat` or `/proc/<pid>/status`

- Find process PID for JVM applications (e.g. Spark): ``` jps | grep SparkSubmit # use this to find pid_Spark_JVM```

- Monitor system usage per process with `pidstat`
  - `pidstat 3 10`  # measure all processes
  - `pidstat -T ALL -p <pid> 10 10` # measure threads of a given pid

- system-wide tools
   - `vmstat 3 10`
   - `mpstat -P ALL 3 10`
   - `sar 3 10`
   - `top`
   - `htop`
   - `atop`
   - `dstat`

- tiptop
   - measures CPU metrics, including IPC, can be run with -p <pid> option

- Measure I/O per pid
  - `pidstat -d -T ALL -p <pid> 3 10`  # measure also I/O
  - `iotop -p <pid> 3 10`
  
- Measure I/O
  - `sar -d 3 10`
  - `iostat -xc 3 10`

- Network
  - `sar -n DEV 3 10`
  - `nethogs` # per-process metrics
  - `iftop` # per-process metrics

- Config info
  - `dmidecode`
  - `/proc/cpuinfo`, `/proc/meminfo`
  - `cpupower frequency-info`
  - `turbostat --debug`
  - `lspci`, `lscpu`, `lsscsi`, `lsblk`

- Tracing, monitoring, debugging
  - `strace -f -p <pid>`
  - JVM jtools: `jstack <pid>`, `jmap`, `jvisualvm`, `jdb`, `jconsole`
  - gdb  

- Dynamic tracing and tool kits

  - perf-tools **https://github.com/brendangregg/perf-tools**
    - cachestat, iosnoop, ..., **https://github.com/brendangregg/perf-tools/tree/master/bin**
    - funccount -d 5 'sys_read'
    - bin/syscount -cp <pid>
  - perf http://www.brendangregg.com/perf.html
  - **BPF-based performance tools**
    - bcc-tools: https://github.com/iovisor/bcc and https://github.com/iovisor/bcc/tree/master/tools
    - bpftrace: https://github.com/iovisor/bpftrace
    - see also https://github.com/goldshtn/linux-tracing-workshop
  - Ftrace
  
- Misc
  - https://github.com/LucaCanali/Linux_tracing_scripts

