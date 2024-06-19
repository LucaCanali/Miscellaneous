# How specify a custom Java Home/Java version for Spark executors on YARN

The problem this solves is to deploy Spark executors on YARN using a JVM version
different from the default for the cluster machines.   
For example, you want to run Spark with Java 17, while your Hadoop cluster is using Java 8 or Java 11 

1. Install the desired version of Java on all nodes of the cluster under the same mount point.
You can copy the files locally on all machines or use a shared filesystem mounted on all nodes.  
For example Java 17 at `/usr/lib/jvm/java-17-openjdk`

NOTE: When running Spark in client mode (default), set JAVA_HOME on the driver too:  
`export JAVA_HOME=/usr/lib/jvm/java-17-openjdk`

2. Set the JAVA_HOME environment variable on the executors and the application master (container) as follows:

```
bin/spark-submit --master yarn \
  --conf spark.yarn.appMasterEnv.JAVA_HOME=/usr/lib/jvm/java-17-openjdk 
  --conf spark.executorEnv.JAVA_HOME=/usr/lib/jvm/java-17-openjdk
```

Note: to avoid using --conf each time, you can persist the parameters in `spark-defaults.conf`
located in `$SPARK_CONF_DIR`

---
If installing the desired JAVA HOME on YARN nodes is not possible, one can send to YARN
the JAVA HONE as a compressed tarball.  
Example:

- Tarball of the desired JAVA: `OpenJDK21U-jdk_x64_linux_hotspot_21.0.3_9.tar.gz`

- Configure JAVA on the driver (for client mode, the default)
  ```
  tar xfz OpenJDK21U-jdk_x64_linux_hotspot_21.0.3_9.tar.gz
  export JAVA_HOME=`pwd`/OpenJDK21U-jdk_x64_linux_hotspot_21.0.3_9.tar.gz/jdk-21.0.3+9
  ```

- Run Spark and upload the tarball with the JAVA HOME, note the PATH names
  ```
  ./bin/spark-shell --master yarn \
    --archives OpenJDK21U-jdk_x64_linux_hotspot_21.0.3_9.tar.gz \
    --conf spark.yarn.appMasterEnv.JAVA_HOME=./OpenJDK21U-jdk_x64_linux_hotspot_21.0.3_9.tar.gz/jdk-21.0.3+9 \
    --conf spark.executorEnv.JAVA_HOME=./OpenJDK21U-jdk_x64_linux_hotspot_21.0.3_9.tar.gz/jdk-21.0.3+9
   ```
  