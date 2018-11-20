# Apache Spark Task Metrics

### This pages describes Spark Executor Task Metrics
Spark executor task metrics provide instrumentation for workload measurements. They are exposed by the Spark WebUI,
Spark History server, Spark EventLog file and from the ListenerBus infrastructure. 
The metrics are provided by each tasks and can be aggregated at higher level )stage level, job level, etc).
A short description of the metrics can be found in the 
[Spark Core Executor source code](https://github.com/apache/spark/tree/master/core/src/main/scala/org/apache/spark/executor).
I sum up here relevant details. 
See also the work on [sparkMeasure](https://github.com/LucaCanali/sparkMeasure) for further details.  
Note: following work on [SPARK-25170](https://issues.apache.org/jira/browse/SPARK-25170) this is now available in the Spark doc: [Spark Task Metrics](https://spark.apache.org/docs/latest/monitoring.html#executor-task-metrics)
  

<table class="table">
  <tr><th>Spark Executor Task Metric name</th>
      <th>Short description</th>
  </tr>
  <tr>
    <td>executorRunTime</td>
    <td>Time the executor spent running this task. This includes time fetching shuffle data.
    The value is expressed in milliseconds.</td>
  </tr>
  <tr>
    <td>executorCpuTime
    <td>CPU Time the executor spent running this task. This includes time fetching shuffle data.
    The value is expressed in nanoseconds.
  </tr>
  <tr>
    <td>executorDeserializeTime</td>
    <td>Time taken on the executor to deserialize this task.
    The value is expressed in milliseconds.</td>
  </tr>
  <tr>
    <td>executorDeserializeCpuTime</td>
    <td>CPU Time taken on the executor to deserialize this task.
     The value is expressed in nanoseconds.</td>
  </tr>
  <tr>
    <td>resultSize</td>
    <td>The number of bytes this task transmitted back to the driver as the TaskResult.</td>
  </tr>
  <tr>
    <td>jvmGCTime</td>
    <td>Amount of time the JVM spent in garbage collection while executing this task.
    The value is expressed in milliseconds.</td>
  </tr>
  <tr>
    <td>resultSerializationTime</td>
    <td>Amount of time spent serializing the task result.
    The value is expressed in milliseconds.</td>
  </tr>
  <tr>
    <td>memoryBytesSpilled</td>
    <td>The number of in-memory bytes spilled by this task.</td>
  </tr>
  <tr>
    <td>diskBytesSpilled</td>
    <td>The number of on-disk bytes spilled by this task.</td>
  </tr>
  <tr>
    <td>peakExecutionMemory</td>
    <td>Peak memory used by internal data structures created during shuffles, aggregations and
        joins. The value of this accumulator should be approximately the sum of the peak sizes
        across all such data structures created in this task. For SQL jobs, this only tracks all
         unsafe operators and ExternalSort.</td>
  </tr>
  <tr>
    <td>inputMetrics.*
    </td>
    <td>Metrics related to reading data from [[org.apache.spark.rdd.HadoopRDD]] 
    or from persisted data.
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.bytesRead</td>
    <td>Total number of bytes read.</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.recordsRead
    </td>
    <td>Total number of records read.</td>
  </tr>
  <tr>
    <td>outputMetrics.*
    </td>
    <td>Metrics related to writing data externally (e.g. to a distributed filesystem), defined only 
            in tasks with output.            
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.bytesWritten</td>
    <td>Total number of bytes written</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.recordsWritten</td>
    <td>Total number of records written</td>
  </tr>
  <tr>
    <td>shuffleReadMetrics.*</td>
    <td>Metrics related to shuffle read operations.</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.recordsRead</td>
    <td>Number of records read in shuffle operations</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.remoteBlocksFetched</td>
    <td>Number of remote blocks fetched in shuffle operations</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.localBlocksFetched</td>
    <td>Number of local (as opposed to read from a remote executor)
    blocks fetched in shuffle operations</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.totalBlocksFetched</td>
    <td>Number of blocks fetched in shuffle operations (both local and remote)</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.remoteBytesRead</td>
    <td>Number of remote bytes read in shuffle operations</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.localBytesRead</td>
    <td>Number of bytes read in shuffle operations from local disk
    (as opposed to read from a remote executor)</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.totalBytesRead</td>
    <td>Number of bytes read in shuffle operations (both local and remote)</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.remoteBytesReadToDisk</td>
    <td>Number of remote bytes read to disk in shuffle operations.
    Large blocks are fetched to disk in shuffle read operations, as opposed to 
    being read into memory, which is the default behavior.</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.fetchWaitTime</td>
    <td>Time the task spent waiting for remote shuffle blocks. 
        This only includes the time blocking on shuffle input data.
        For instance if block B is being fetched while the task is still not finished 
        processing block A, it is not considered to be blocking on block B.
        The value is expressed in milliseconds.</td>
  </tr>
  <tr>
    <td>shuffleWriteMetrics.*</td>
    <td>Metrics related to operations writing shuffle data.</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.bytesWritten</td>
    <td>Number of bytes written in shuffle operations</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.recordsWritten</td>
    <td>Number of records written in shuffle operations</td>
  </tr>
  <tr>
    <td>&nbsp;&nbsp;&nbsp;&nbsp;.writeTime</td>
    <td>Time spent blocking on writes to disk or buffer cache.
    The value is expressed in nanoseconds.</td>
  </tr>
</table>