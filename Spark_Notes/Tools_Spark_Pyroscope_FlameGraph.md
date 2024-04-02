# How-to profile Apache Spark jobs using Grafana Pyroscope

## Topic
This note describes how to use [Grafana Pyroscope](https://grafana.com/oss/pyroscope/) to profile Apache Spark
job executions. By the end, you'll have a deeper understanding of profiling Spark executor, Flame Graph visualizations,
and how they can provide an advanced toolset to troubleshoot and optimize Spark workload performance.

See also the blog post 
[Enhancing Apache Spark Performance with Flame Graphs: A Practical Example Using Grafana Pyroscope](https://db-blog.web.cern.ch/node/193)

## Why Should You Profile Using Flame Graphs?

- **Visual Insight**: The [Flame Graph](https://www.brendangregg.com/flamegraphs.html) provides a graphical 
  representation of stack profiles. This technique offers an edge in troubleshooting Spark workloads and
  goes hand in hand with the standard tools like the [Spark WebUI](https://spark.apache.org/docs/latest/web-ui.html)
  and the [Spark metrics dashboard](https://github.com/cerndb/spark-dashboard)
- **Identifying CPU-intensive Methods**: Flame Graphs pinpoint "hot methods" that heavily consume CPU, allowing
  developers to optimize those specific areas.
- **Multifaceted Profiling**: Beyond CPU usage, Flame Graphs can also profile time spent on waiting (off CPU time), and memory
  allocation. This feature is particularly beneficial when diagnosing I/O, network, and memory issues.

## Why Choose Pyroscope?
- **Streamlined Data Collection & Visualization**: The [Pyroscope project page](https://grafana.com/oss/pyroscope/) 
  offers a simplified approach to data gathering and visualization with its custom WebUI and agent integration.
- **Java Integration**: The [Pyroscope java agent](https://grafana.com/docs/pyroscope/latest/configure-client/language-sdks/java/)
  is tailored to work seamlessly with Spark. This integration shines especially when Spark is running on various
  clusters such as YARN, K8S, or standalone Spark clusters.
- **Correlation with Grafana**: Grafana’s integration with Pyroscope lets you juxtapose metrics with other 
  instruments, including the [Spark metrics dashboard](https://github.com/cerndb/spark-dashboard).
- **Proven Underlying Technology**: For Java and Python, the tech essentials for collecting stack profiling data,
  [async-profiler and py-spy](https://github.com/LucaCanali/Miscellaneous/blob/master/Spark_Notes/Tools_Spark_Linux_FlameGraph.md), 
  are time-tested and reliable.
- **Functional & Detailed WebUI**: Pyroscope’s WebUI stands out with features that allow users to:
  - Select specific data periods
  - Store and display data across various measurements
  - Offer functionalities to contrast and differentiate measurements
  - Showcase collected data for all Spark executors, with an option to focus on individual executors or machines
- **Lightweight Data Acquisition**: The Pyroscope java agent is efficient in data gathering. By default, stacks are 
  sampled every 10 milliseconds and uploaded every 10 seconds. We did not observe any measurable
  performance or stability impact of the instrumentation.

---
## Pyroscope for Spark in 3 easy steps
### 1. Start Pyroscope 
  - Download from https://github.com/grafana/pyroscope/releases 
  - CLI start: `./pyroscope -server.http-listen-port 5040`
  - Or use docker: `docker run -it -p 5040:4040 grafana/pyroscope`  
  - Note: customize the port number, I used port 5040 to avoid confusion with the Spark WebUI which defaults to port 4040 too
  - [Pyroscope doc](https://grafana.com/docs/pyroscope/latest/get-started/) has more details including how to use Pyroscope with Helm
### 2. Configure the Spark executors to send metrics to Pyroscope
  - 3 different alternative methods are described in later in note
### 3. Open the browser to the Pyroscope WebUI and analyze data from there
  - data can also be exported to a Grafana dashboard, see the [doc](https://grafana.com/docs/pyroscope/latest/)
    
## Spark configuration for the Pyroscope Java agent
This describes 3 different and alternative methods to configure Spark to use Pyroscope

### A. Spark in local mode
When using Spark in local mode, typically for development, you just need to configure the java agent:
- Build or download the latest version of the pyroscope java agent, for example:
  - `wget https://repo1.maven.org/maven2/io/pyroscope/agent/0.13.0/agent-0.13.0.jar`
- Configure using environment variables, 
  see also [java client configuration options](https://grafana.com/docs/pyroscope/latest/configure-client/language-sdks/java/#java-client-configuration-options):
  ```
  export PYROSCOPE_APPLICATION_NAME=my.Spark.app
  export PYROSCOPE_SERVER_ADDRESS="http://<myhostname>:5040" # match to the server and port used when starting Pyroscope
  ``` 
- Run Spark (PySpark, spark-submit, spark-shell,...) in local mode and configure the java agent:
  - `bin/spark-shell --master local[*] --driver-java-options "-javaagent:./agent-0.13.0.jar"`
    - note, match to the downloaded agent jar name and path 

### B. Spark on a cluster (YARN, Kubernetes, Standalone) with java agent
When using Spark on cluster resources, most of the interesting processing happens of the executors,
which are JVMs launched on the cluster resources.
This example shows how to do this with a java agent (see also below a different method using Spark plugins).  
Configuration needs to be set up for the executors, as environment variables on the executor's processes, 
for doing this we use Spark's `--conf spark.executorEnv.ENVNAME=value`.  
The server and port where you started Pyroscope needs to be accessible by all the executors (check that you don't have firewall rules blocking this).

```
export PYROSCOPE_APPLICATION_NAME=my.Spark.app
export PYROSCOPE_SERVER_ADDRESS="http://<myhostname>:5040" # match to the server and port used when starting Pyroscope
export PYROSCOPE_PROFILER_EVENT=itimer # other options: wall, alloc
export PYROSCOPE_LABELS='hostname=`hostname`'

bin/spark-shell --master yarn \ # edit master type when usingr k8s or a standalone cluster
--packages io.pyroscope:agent:0.13.0 \ # update to the agent's latest version
--conf spark.executor.extraJavaOptions="-javaagent:./io.pyroscope_agent-0.13.0.jar" \ # match to the agent version
--conf spark.executorEnv.PYROSCOPE_APPLICATION_NAME=$PYROSCOPE_APPLICATION_NAME \
--conf spark.executorEnv.PYROSCOPE_LABELS=$PYROSCOPE_LABELS \
--conf spark.executorEnv.PYROSCOPE_PROFILER_EVENT=$PYROSCOPE_PROFILER_EVENT \
--conf spark.executorEnv.PYROSCOPE_SERVER_ADDRESS=$PYROSCOPE_SERVER_ADDRESS 
```

### C. Spark on a cluster with Spark executor plugins

This method uses Spark plugins to configure Spark executors to send metrics to the Pyroscope server.  
Spark plugins provide an interface, and related configuration, for injecting custom code on executors 
as they are initialized.  
Here we use a custom plugin developed and shared with the repo [SparkPLugins](https://github.com/cerndb/SparkPlugins)  
The jars are available via [maven central](https://mvnrepository.com/artifact/ch.cern.sparkmeasure/spark-plugins)  

Spark configuration parameters:
- Set up the use of the plugin jars
  ``` 
  --packages ch.cern.sparkmeasure:spark-plugins_2.12:0.3 (also available for scala 2.13)
  --conf spark.plugins=ch.cern.PyroscopePlugin
  ```

Additional fine-tuning configuration parameters:
``` 
--conf spark.pyroscope.server=.. - > default "http://localhost:4040", update to match the server name and port used by Pyroscope
--conf spark.pyroscope.applicationName -> default spark.conf.get("spark.app.id")`
--conf spark.pyroscope.eventType -> default ITIMER, possible values ITIMER, CPU, WALL, ALLOC, LOCK
```

**Example:**  
An example of how to put all the configuration together and start Spark on a cluster with Pyroscope Flame Graph 
continuous monitoring. Example:  
```
# Start Pyroscope
./pyroscope -server.http-listen-port 5040
# docker run -it -p 5040:4040 grafana/pyroscope

# Spark Spark (spark-shell, PySpark, spark-submit
bin/spark-shell --master yarn  \
  --packages ch.cern.sparkmeasure:spark-plugins_2.12:0.3,io.pyroscope:agent:0.13.0 \ # update with latest versions
  --conf spark.plugins=ch.cern.PyroscopePlugin \
  --conf spark.pyroscope.server="http://<myhostname>:5040" # match to the server and port used when starting Pyroscope
```

This is an example of how to use the configuration programmatically (using PySpark):
```
from pyspark.sql import SparkSession

# Get the Spark session
spark = (SparkSession.builder.
      appName("Instrumented app").master("yarn")
      .config("spark.executor.memory","16g")
      .config("spark.executor.cores","4")
      .config("spark.executor.instances", 2)
      .config("spark.jars.packages", "ch.cern.sparkmeasure:spark-plugins_2.12:0.3,io.pyroscope:agent:0.13.0")
      .config("spark.plugins", "ch.cern.PyroscopePlugin")
      .config("spark.pyroscope.server", "http://<myhostname>:5040")
      .getOrCreate()
    )
```

----
## Details on the configuration of the Profiler mode
Pyroscope agent for Java uses [async-profiler](https://github.com/async-profiler/async-profiler) under the
hood, see also [async-profiler for Spark](https://github.com/LucaCanali/Miscellaneous/blob/master/Spark_Notes/Tools_Spark_Linux_FlameGraph.md).  
The main profiling modes of interest are (see [doc](https://github.com/async-profiler/async-profiler) for details):
- `itimer` - profiles CPU usage (default)
- `cpu` - profiles CPU with the addition of kernel stack traces, however requires perf_events support
- `wall` - profiles wall time, use when measuring workloads with I/O or network events
- `alloc` - profiles memory allocation

## Overhead of profiling the JVM with Pyroscope
- The overhead of continuously profiling the JMV running Spark code with Pyroscope appears to be low 
  to be quite low: when comparing Spark execution time with and without instrumentation we
  did not observe any measurable performance or stability impact of the instrumentation.
  This was observed both locally and when running Spark on a YARN cluster. It appears safe to keep
  the java agent for pyroscope running with production jobs. More investigations and experience
  should be collected to fully validate these conclusions.

----
### Prerequisite: start Pyroscope
- Download from https://github.com/grafana/pyroscope/releases
- CLI start: `./pyroscope -server.http-listen-port 5040`
- Or use docker: `docker run -it -p 5040:4040 grafana/pyroscope`
- Note: customize the port number, I used port 5040 to avoid confusion with the Spark WebUI which defaults to port 4040 too
- [Pyroscope doc](https://grafana.com/docs/pyroscope/latest/get-started/) has more details including how to use Pyroscope with Helm

## Profiling Python UDFs
Example of how to instrument Python UDFs with Pyroscope (and py-spy under the hood):
```
# pip install pyroscope-io if needed
import pyroscope
import socket

pyroscope_server="http://<myyhostname>:5040" # match to the server and port used when starting Pyroscope
app_name = spark.conf.get("spark.app.id")

# basic example of Python udf instrumented with Pyroscope
@udf("int")
def add1(x):
    if globals().get('pyroscope_configured') is None:
        pyroscope.configure(application_name = app_name , server_address = pyroscope_server, tags={"hostname": socket.gethostname()})
        # pyroscope.configure(application_name = app_name , server_address = pyroscope_server, report_pid=True)
        globals()['pyroscope_configured'] = True
    return x + 1
```

## Overhead of profiling Python UDFs with Pyroscope
- The first tests show that the overhead of profiling Python UDF in this way is potentially 
  quite high, in some circumstances, this needs further studies.
