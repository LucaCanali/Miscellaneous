# Spark Dropwizard metrics instrumentation

Spark is instrumented with the Dropwizard/Codahale metrics library.
Several components of Spark are instrumented, notable for this work several metrics generating 
from Spark driver and executors components can be instrumented. 

An important architectural details is that the metrics are sent directly from the sources to the sink.
This is important when running on a cluster, as each executor will communicate directly to the sink, for better scalability. 

Contrast this to the standard WebUI/Eventlog instrumentation of Spark, which uses Listeners 
and where metrics will flow through the driver (see the architecture diagram of sparkMeasure 
for example).

## Instrumented components
- master: The Spark standalone master process.
- applications: A component within the master which reports on various applications.
- worker: A Spark standalone worker process.
- executor: A Spark executor.
- driver: The Spark driver process (the process in which your SparkContext is created).
- shuffleService: The Spark shuffle service.
- applicationMaster: The Spark ApplicationMaster when running on YARN.

Metrics used by Spark are of type: gauge, counter, histogram, meter and timer
(see dropwizard documentation for details)[https://metrics.dropwizard.io/4.0.0/manual/core.html].
The following list documents the metrics available, grouped per component
 instance and source namespace.
The most common time of metrics used in Spark instrumentation are gauges and counters. 
Counters can be recognized as they have the `.count` suffix. Timers, meters and histograms are annotated in the list,
the default is that a metric is a gauge.
Some of the metrics is the list are only active if a corresponding Spark configuration parameters
is used to enable them, as detailed in the list.

### Component instance = Driver
This is the component with the largest amount of instrumented metrics

- namespace=BlockManager
  - disk.diskSpaceUsed_MB
  - memory.maxMem_MB
  - memory.maxOffHeapMem_MB
  - memory.maxOnHeapMem_MB
  - memory.memUsed_MB
  - memory.offHeapMemUsed_MB
  - memory.onHeapMemUsed_MB
  - memory.remainingMem_MB
  - memory.remainingOffHeapMem_MB
  - memory.remainingOnHeapMem_MB

- namespace=HiveExternalCatalog
  - fileCacheHits.count
  - filesDiscovered.count
  - hiveClientCalls.count
  - parallelListingJobCount.count
  - partitionsFetched.count

- namespace=CodeGenerator
  - compilationTime (histogram)
  - generatedClassSize (histogram)
  - generatedMethodSize (histogram)
  - hiveClientCalls.count
  - sourceCodeSize (histogram)

- namespace=DAGScheduler
  - job.activeJobs 
  - job.allJobs
  - messageProcessingTime (timer)
  - stage.failedStages
  - stage.runningStages
  - stage.waitingStages

- namespace=LiveListenerBus
  - listenerProcessingTime.org.apache.spark.HeartbeatReceiver (timer)
  - listenerProcessingTime.org.apache.spark.scheduler.EventLoggingListener (timer)
  - listenerProcessingTime.org.apache.spark.status.AppStatusListener (timer)
  - numEventsPosted.count
  - queue.appStatus.listenerProcessingTime (timer)
  - queue.appStatus.numDroppedEvents.count
  - queue.appStatus.size
  - queue.eventLog.listenerProcessingTime (timer)
  - queue.eventLog.numDroppedEvents.count
  - queue.eventLog.size
  - queue.executorManagement.listenerProcessingTime (timer)

- namespace=appStatus (all metrics of type=counter)
  - **note:** Introduced in Spark 3.0. Conditional to configuration parameter:  
   `spark.app.status.metrics.enabled=true` (default is false)
  - stages.failedStages.count
  - stages.skippedStages.count
  - tasks.blackListedExecutors.count
  - tasks.completedTasks.count
  - tasks.failedTasks.count
  - tasks.killedTasks.count
  - tasks.skippedTasks.count
  - tasks.unblackListedExecutors.count
  - jobs.succeededJobs
  - jobs.failedJobs
  - jobDuration
  
- namespace=AccumulatorSource  
  - **note:** User-configurable sources to attach accumulators to metric system
  - DoubleAccumulatorSource
  - LongAccumulatorSource

- namespace=spark.streaming
  - **note** applies to Spark Streaming only. Conditional to configuration parameter:
  `spark.sql.streaming.metricsEnabled= true` (default false) 
  - eventTime-watermark
  - inputRate-total
  - latency
  - processingRate-total
  - states-rowsTotal
  - states-usedBytes

### Component instance = Executor
These metrics are exposed by Spark executors. Note, currently they are not available
when running in local mode.
 
- namespace=executor (metrics are of type counter or gauge)
  - bytesRead.count
  - bytesWritten.count
  - cpuTime.count
  - deserializeCpuTime.count
  - deserializeTime.count
  - diskBytesSpilled.count
  - filesystem.file.largeRead_ops
  - filesystem.file.read_bytes
  - filesystem.file.read_ops
  - filesystem.file.write_bytes
  - filesystem.file.write_ops
  - filesystem.hdfs.largeRead_ops
  - filesystem.hdfs.read_bytes
  - filesystem.hdfs.read_ops
  - filesystem.hdfs.write_bytes
  - filesystem.hdfs.write_ops
  - jvmCpuTime
  - jvmGCTime.count
  - memoryBytesSpilled.count
  - recordsRead.count
  - recordsWritten.count
  - resultSerializationTime.count
  - resultSize.count
  - runTime.count
  - shuffleBytesWritten.count
  - shuffleFetchWaitTime.count
  - shuffleLocalBlocksFetched.count
  - shuffleLocalBytesRead.count
  - shuffleRecordsRead.count
  - shuffleRecordsWritten.count
  - shuffleRemoteBlocksFetched.count
  - shuffleRemoteBytesRead.count
  - shuffleRemoteBytesReadToDisk.count
  - shuffleTotalBytesRead.count
  - shuffleWriteTime.count
  - threadpool.activeTasks
  - threadpool.completeTasks
  - threadpool.currentPool_size
  - threadpool.maxPool_size

- namespace=NettyBlockTransfer
  - shuffle-client.usedDirectMemory
  - shuffle-client.usedHeapMemory
  - shuffle-server.usedDirectMemory
  - shuffle-server.usedHeapMemory

- namespace=HiveExternalCatalog
  - fileCacheHits.count
  - filesDiscovered.count
  - hiveClientCalls.count
  - parallelListingJobCount.count
  - partitionsFetched.count

- namespace=CodeGenerator
  - compilationTime (histogram)
  - generatedClassSize (histogram)
  - generatedMethodSize (histogram)
  - hiveClientCalls.count
  - sourceCodeSize (histogram)

### Source = JVM Source 
**Note:** this applies to driver and executor (and other components)
Provides information from JVM metrics, notably inclusing usage of memory.
Activate with: `spark.metrics.conf.*.source.jvm.class=org.apache.spark.metrics.source.JvmSource`

- namespace=jvm
  - PS-MarkSweep.count
  - PS-MarkSweep.time
  - PS-Scavenge.count
  - PS-Scavenge.time
  - direct.capacity
  - direct.count
  - direct.used
  - heap.committed
  - heap.init
  - heap.max
  - heap.usage
  - heap.used
  - mapped.capacity
  - mapped.count
  - mapped.used
  - non-heap.committed
  - non-heap.init
  - non-heap.max
  - non-heap.usage
  - non-heap.used
  - pools.Code-Cache.committed
  - pools.Code-Cache.init
  - pools.Code-Cache.max
  - pools.Code-Cache.usage
  - pools.Code-Cache.used
  - pools.Compressed-Class-Space.committed
  - pools.Compressed-Class-Space.init
  - pools.Compressed-Class-Space.max
  - pools.Compressed-Class-Space.usage
  - pools.Compressed-Class-Space.used
  - pools.Metaspace.committed
  - pools.Metaspace.init
  - pools.Metaspace.max
  - pools.Metaspace.usage
  - pools.Metaspace.used
  - pools.PS-Eden-Space.committed
  - pools.PS-Eden-Space.init
  - pools.PS-Eden-Space.max
  - pools.PS-Eden-Space.usage
  - pools.PS-Eden-Space.used
  - pools.PS-Old-Gen.committed
  - pools.PS-Old-Gen.init
  - pools.PS-Old-Gen.max
  - pools.PS-Old-Gen.usage
  - pools.PS-Old-Gen.used
  - pools.PS-Survivor-Space.committed
  - pools.PS-Survivor-Space.init
  - pools.PS-Survivor-Space.max
  - pools.PS-Survivor-Space.usage
  - pools.PS-Survivor-Space.used
  - total.committed
  - total.init
  - total.max
  - total.used

### Component instance = applicationMaster
Note: applies when running on YARN

- numContainersPendingAllocate
- numExecutorsFailed
- numExecutorsRunning
- numLocalityAwareTasks
- numReleasedContainers

### Component instance = mesos_cluster
Note: applies when running on mesos
- waitingDrivers
- launchedDrivers
- retryDrivers

### Component instance = master
Note: applies when running in Spark standalone as master

- workers
- aliveWorkers
- apps
- waitingApps

### Component instance = ApplicationSource
Note: applies when running in Spark standalone as master

- status
- runtime_ms
- cores

### Component instance = worker
Note: applies when running in Spark standalone as worker

- executors
- coresUsed
- memUsed_MB
- coresFree
- memFree_MB

## Component instance = shuffleService
Note: applies to the shuffle service

- blockTransferRateBytes (meter)
- numActiveConnections.count
- numRegisteredConnections.count
- openBlockRequestLatencyMillis (histogram)
- registerExecutorRequestLatencyMillis (histogram)
- registeredExecutorsSize
- shuffle-server.usedDirectMemory
- shuffle-server.usedHeapMemory
