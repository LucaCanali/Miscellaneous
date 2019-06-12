# How specify a custom Java Home/Java version for Spark executors on YARN

The problem this solves is to deploy Spark executors on YARN using a JVM version
different than the default for the cluster machines.   
This note comes from the experience of running Spark on a legacy cluster still using Java 7 + 

1. Install the desired version of Java on all nodes of the cluster under the same mount point.
You can copy the files on all machines or use a mounted filesystem.  
For example jdk 1.8 under /usr/lib/jvm/java-oracle or /usr/lib/jvm/java-openjdk

2. Set the JAVA_HOME environment variable on the executors and the application master (container) as follows:

```
bin/spark-shell --conf spark.yarn.appMasterEnv.JAVA_HOME=/usr/lib/jvm/java-oracle --conf spark.executorEnv.JAVA_HOME=/usr/lib/jvm/java-oracle
```

2b. When running in client mode, set JAVA_HOME on the driver too.

Note: to avoid using --conf each time, you can persist the parameters in `spark-defaults.conf` (in `$SPARK_CONF_DIR`)

---
