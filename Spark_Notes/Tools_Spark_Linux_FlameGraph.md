# Flame Graphs for Spark - Tools and Notes

In this note you can find a few links and basic examples relevant to using Flame Graphs for profiling Apache Spark workloads
running in the JVM on Linux.

## TL;DR use async-profiler for JVM and py-spy for Python

**Link to [async-profiler on GitHub](https://github.com/jvm-profiling-tools/async-profiler)**. Build async profiler as in the README:
 - `export JAVA_HOME=..` to a valid JDK and 
 - run `make`  
 
**Example** of how to use async profiler for Spark
 
- Simple test in local mode (`bin/spark-shell --master local[*]`)
 
- First find the pid of the JVM running Spark driver and executor, example:
```aidl
$ jps
171657 SparkSubmit
```

- Profile JVM and create the FlameGraph:
```
# profile by time (regardless if process is on CPU or waiting)
./profiler.sh -e wall -d 30 -f $PWD/flamegraph1.svg <pid_of_JVM>

# profile on-CPU threads, without using perf
./profiler.sh -e itimer -d 30 -f $PWD/flamegraph1.svg <pid_of_JVM>
```

- Visualize the JVM execution FlameGraph:
```
firefox flamegraph1.svg
```
- Drill down to the part of the FlameGraph of interest (click on svg to zoom in), for example:
zoom in to `java/util/concurrent/ThreadPoolExecutor$Worker.run` +
 further zoom in to `org/apache/spark/executor/Executor$TaskRunner.run`

If you want to use CPU profiling (or profiling other per events) using perf (mode `-e cpu` you need also
to set the following and run profiling as root:
```
# echo 1 > /proc/sys/kernel/perf_event_paranoid
# echo 0 > /proc/sys/kernel/kptr_restrict
```

**Python:**
Profile Python code with flame graph for Spark when using PySpark and Python UDF, for example.
A good tool to use is [py-spy](https://github.com/benfred/py-spy):  
Install and example:
```python
pip install py-spy
py-spy -p <pid> -f <flamegraph_file>
```

### FlameGraph and Async JVM stack profiling for Spark on YARN
Profile one executor, example:
 - First, find the executor hostname and pid, for example use Spark WebUI or run `sc.getExecutorMemoryStatus`  
 - With `ps` or `jps -v` find pid of the executor process, on YARN Spark 3.0 uses the class`YarnCoarseGrainedExecutorBackend`,
  on Spark 2.4 is instead `CoarseGrainedExecutorBackend`
 - Profile the executor pid as detailed above 

### FlameGraph and Async JVM stack profiling for Spark on Kubernetes
How to profile one executor, example:
 - Identify a Kubernetes pod to profile `kubectl get pods -n yournamspace`
 - copy async profiler from driver to executor:
 `kubectl cp async-profiler-1.6 <pod_name_here>:/opt/spark/work-dir`
 - run profiler as described above, in `-e wall` or `-e itimer` mode
 - using async profiler with perf in `-e cpu` mode, is also possible, ideally running from host system/VM, [details here](https://github.com/jvm-profiling-tools/async-profiler#profiling-java-in-a-container) 

## Context

Stack profiling and on-CPU Flame Graph visualization are very useful tools and techniques for investigating CPU workloads.   
See [Brendan Gregg's page on Flame Graphs](http://www.brendangregg.com/flamegraphs.html)   
Stack profiling is useful for understanding and drilling-down on "hot code": 
you can use it to find parts of the code using considerable amount of time and provide insights for troubleshooting.
FlameGraph visualization of the stack profiles brings additional value, including the fact of 
being an appealing interface and providing context about the running the code, by showing for example the parent functions.


The main challenge that several tools undertake for profiling the JVM is on how to collect stack frames
precisely and with low overhead.
For more details related to the challenges of profiling Java/JVM see 
- [Nitsan Wakart](https://twitter.com/nitsanw): [Using FlameGraphs To Illuminate The JVM by](https://en.wikipedia.org/wiki/DTracehttps://www.youtube.com/watch?v=ugRrFdda_JQ), [Exploring Java Perf Flamegraphs](https://2017.javazone.no/program/56179b136b91458a843383e13fd2efa1)
- [Brendan Gregg](https://twitter.com/brendangregg): [Java in Flames](https://medium.com/netflix-techblog/java-in-flames-e763b3d32166)

## A list of profilers relevant for troubleshooting Spark workloads

- [async-profiler](https://github.com/jvm-profiling-tools/async-profiler) (see also an example of usage later in this note)
  - based on AsyncGetCallTrace, also has perf events
  - no need to install agents
  - info from the tool's author: [Andrei Pangin](https://twitter.com/AndreiPangin): [Everything you wanted to know about Stack Traces and Heap Dumps](https://2017.javazone.no/program/c5577d90198b474cbf14c7867209d96c)
  - more info at [http://psy-lob-saw.blogspot.ch/2017/02/flamegraphs-intro-fire-for-everyone.html]
  - see also this [http://blogs.microsoft.co.il/sasha/2017/07/07/profiling-the-jvm-on-linux-a-hybrid-approach/]
  - issues with sampling at safepoint: [http://psy-lob-saw.blogspot.ch/2016/02/why-most-sampling-java-profilers-are.html]
- [honest-profiler](https://github.com/jvm-profiling-tools/honest-profiler)
  - also based on AsyncGetCallTrace, deploy an agent on the JVM, which allows also remote control
- methods based on Java Flight Recorder
  - See [https://gist.github.com/kayousterhout/7008a8ebf2babeedc7ce6f8723fd1bf4]
  - an example at [Apache Spark 2.0 Performance Improvements Investigated With Flame Graphs](https://externaltable.blogspot.com/2016/09/spark-20-performance-improvements.html): 
  - only measures the JVM
  - needs also [https://github.com/lhotari/jfr-report-tool]
  - JFR requires license from Oracle if used in production up to Java version 1.8, for Java 9 and higher
  I understand with is now in open source
- Perf
  - see Brendan's pages and the blog post [Java in Flames](https://medium.com/netflix-techblog/java-in-flames-e763b3d32166) 
  - goes together with [perf-map-agent](https://github.com/jvm-profiling-tools/perf-map-agent)
  - See also [Profiling JVM applications](https://developer.lightbend.com/blog/2018-04-09-profiling-JVM-applications/)
  - perf is a great tool, but not my favourite method for Spark profiling, as many functions appear listed as "interpreter" and cannot be resolved by this method.
  - see also the additional JVM options when running Spark (see examples below)
- method with the statsd-jvm-profiler
  - see [Spark in Flames](https://www.paypal-engineering.com/2016/09/08/spark-in-flames-profiling-spark-applications-using-flame-graphs/)
  - note, I have not yet tested this
- Methods based on jstack
  - run [jstack](http://docs.oracle.com/javase/7/docs/technotes/tools/share/jstack.html) on the executors at low frequency for profiling has high overhead. Typically you would do this manually to get an idea of a stuck process. Similarly one can dump executors stack traces "manually" from the WebUI 
  - I understood that Facebook used a jstack-sampling method for their flamegraph, as reported at the Spark Summit
   Europe 2016 talk [Apache Spark at Scale: A 60 TB+ Production Use Case by Sital Kedia](https://www.slideshare.net/SparkSummit/spark-summit-eu-talk-by-sital-kedia) Reported to hav
- Many commercial tools exist that provide profiling 
  - the talk [Using FlameGraphs To Illuminate The JVM by Nitsan Wakart](Using FlameGraphs To Illuminate The JVM by Nitsan Wakart)
    lists some of the tools 
  - most commercial profiling tool report prole data as trees
  - most commercial profiling tools use SafePoints rather than AsyncGetCallTrace
- Distributed Hadoop Profiler [HProfiler](https://github.com/cerndb/Hadoop-Profiler)
  - based on perf, integrates with YARN and aggregates profiles
- Python: [py-spy](https://github.com/benfred/py-spy)
---
## Flame Graph repo:
Download: ```git clone https://github.com/brendangregg/FlameGraph```

## Example of usage of async-profiler  

Download from [https://github.com/jvm-profiling-tools/async-profiler]   
Build as in the README (export JAVA_HOME and make)  
Find the pid of the JVM runnign the Spark executor, example:
```aidl
$ jps
171657 SparkSubmit
171870 Jps
```

Profile JVM and create the flamegraph, example:
```
./profiler.sh -d 30 -f $PWD/flamegraph1.svg <pid_of_JVM>
```

Visualize the on-CPU flamegraph:
```
firefox flamegraph1.svg
```

Example of the output:   
[Click here to get the SVG version of the on-CPU Flamegraph](https://canali.web.cern.ch/canali/svg/Flamegraph_Spark_SQL_read_CPU-bound.svg)
![Example](https://1.bp.blogspot.com/-HMAOBL9gl58/Wcy7HBUBghI/AAAAAAAAFAw/YrvKqOGhSwEn9QuOAQqBJvoKNn7IweiuQCLcBGAs/s1600/Flamegraph_Spark_SQL_read_CPU-bound_javacolors.PNG)

---
async-profiler by default records stack traces on CPU events, it can also be configured to record stack traces on other type of events.
The list of available events is available as in this example:
```
./profiler.sh list <pid_of_JVM>

Basic events:
  cpu
  alloc
  lock
  wall
  itimer
Perf events:
  page-faults
  context-switches
  cycles
  instructions
  cache-references
  cache-misses
  branches
  branch-misses
  bus-cycles
  L1-dcache-load-misses
  LLC-load-misses
  dTLB-load-misses
  mem:breakpoint
  trace:tracepoint
```


Example of profile on alloc (heap memory allocation) events
```
./profiler.sh -d 30  -e alloc -f $PWD/flamegraph_heap.svg <pid_of_JVM>
../FlameGraph/flamegraph.pl --colors=mem flamegraph_heap.txt >flamegraph_heap.svg
```
Example output:   
[Click here to get the SVG version of the Heap Flamegraph](https://canali.web.cern.ch/canali/svg/Flamegraph_Spark_SQL_read_Parquet_annotated.svg)
![Example](https://2.bp.blogspot.com/-Bxaa4CCKfx8/Wc60YfC2A5I/AAAAAAAAFBA/aENnOyv-SjQZFkUUMWwJjahrssmdlpekACLcBGAs/s1600/Flamegraph_HEAP_Spark_SQL_read_Parquet.png)

---
## Example of usage of perf for java/Spark:

Get perf-map-agent and build it following instructions at:   
```https://github.com/jvm-profiling-tools/perf-map-agent```

set JAVA_HOME and AGENT_OME for FlameGraph/jmaps

run Spark with extra java options. examples:   
```--conf "spark.driver.extraJavaOptions"="-XX:+PreserveFramePointer"```   
or:  
```--conf "spark.driver.extraJavaOptions"="-XX:+PreserveFramePointer -XX:+UnlockDiagnosticVMOptions -XX:+DebugNonSafepoints"```   
note:  
similarly add options on executors with `--conf "spark.driver.extraJavaOptions"=...` 

Gather data with (example):
```perf record -a -g -F 99 -p <pid> sleep 10; FlameGraph/jmaps```  

Generate the flamegraph:
```perf script |../FlameGraph/stackcollapse-perf.pl | ../FlameGraph/flamegraph.pl > perfFlamegraph1.svg```   


----
## Example of usage of JMC and Java Flight Recorder

Start Spark with the extra Java options (only driver options needed if running in local mode):   
```
--conf "spark.driver.extraJavaOptions"="-XX:+UnlockCommercialFeatures -XX:+FlightRecorder -XX:+UnlockDiagnosticVMOptions -XX:+DebugNonSafepoints -XX:FlightRecorderOptions=stackdepth=1024"
--conf "spark.executor.extraJavaOptions"="-XX:+UnlockCommercialFeatures -XX:+FlightRecorder -XX:+UnlockDiagnosticVMOptions -XX:+DebugNonSafepoints -XX:FlightRecorderOptions=stackdepth=1024"
```

Gather data:   
```
jcmd 146903 JFR.start filename=sparkProfile1.jfr duration=30s
```

Process the Java Flight Recorder file with jfr-report-tool, see instructions at: [https://github.com/lhotari/jfr-report-tool]
```
jfr-report-tool/jfr-report-tool -e none -m 1 sparkProfile3.jfr
```

In alternative can use:   
[https://github.com/chrishantha/jfr-flame-graph]   
jfr-flame-graph/run.sh -f sparkProfile1.jfr -o spark_jfr_out.txt
../FlameGraph/flamegraph.pl spark_jfr_out.txt > perf2.svg

