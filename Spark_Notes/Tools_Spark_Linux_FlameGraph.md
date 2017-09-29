# Flame Graphs for Spark - Tools and Notes

In this note you can find a few links and basic examples relevant to using Flame Graphs for Apache Spark on Linux.

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
  - also no need to install agents
  - read this [http://psy-lob-saw.blogspot.ch/2017/02/flamegraphs-intro-fire-for-everyone.html]
  - and this [http://blogs.microsoft.co.il/sasha/2017/07/07/profiling-the-jvm-on-linux-a-hybrid-approach/]
  - issues with sampling at safepoint: [http://psy-lob-saw.blogspot.ch/2016/02/why-most-sampling-java-profilers-are.html]
- [honest-profiler](https://github.com/jvm-profiling-tools/honest-profiler)
  - also based on AsyncGetCallTrace, deploy an agent on the JVM, which allows also remote control
- methods based on Java Flight Recorder
  - See [https://gist.github.com/kayousterhout/7008a8ebf2babeedc7ce6f8723fd1bf4]
  - an example at [Apache Spark 2.0 Performance Improvements Investigated With Flame Graphs](https://externaltable.blogspot.com/2016/09/spark-20-performance-improvements.html): 
  - only measures the JVM
  - needs also [https://github.com/lhotari/jfr-report-tool]
  - currently requires license from Oracle if used in production, recent announcements hint Oracle fully open sourcing this
- Perf
  - see Brendan's pages and the blog post [Java in Flames](https://medium.com/netflix-techblog/java-in-flames-e763b3d32166) 
  - goes together with [perf-map-agent](https://github.com/jvm-profiling-tools/perf-map-agent)
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

---
## Flame Graph repo:
Download: ```git clone https://github.com/brendangregg/FlameGraph```

## Example of usage of async-profiler  

Download from [https://github.com/jvm-profiling-tools/async-profiler]  
Example of use, stack profile collection in collapsed form:  
```
./profiler.sh -d 30 -o collapsed -f $PWD/flamegraph1.txt <pid_of_JVM>
```

Generate and visualize the on-CPU flamegraph:
```
../FlameGraph/flamegraph.pl --colors=java flamegraph1.txt >flamegraph1.svg

firefox flamegraph1.svg
```

Example of the output:   
[Click here to get the SVG version of the on-CPU Flamegraph](https://canali.web.cern.ch/canali/svg/Flamegraph_Spark_SQL_read_CPU-bound.svg)
![Example](https://1.bp.blogspot.com/-HMAOBL9gl58/Wcy7HBUBghI/AAAAAAAAFAw/YrvKqOGhSwEn9QuOAQqBJvoKNn7IweiuQCLcBGAs/s1600/Flamegraph_Spark_SQL_read_CPU-bound_javacolors.PNG)

---
async-profiler can also do heap profiling which can also be visualized as a flamegrpah (measure where large memory allocations happen). Example:

```
./profiler.sh -d 30  -m heap -o collapsed -f $PWD/flamegraph_heap.txt <pid_of_JVM>

../FlameGraph/flamegraph.pl --colors=mem flamegraph_heap.txt >flamegraph_heap.svg
```
Example of the output:   
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

