# Apache Spark metrics sink to graphite

Spark is instrumented with dropwizard/codahale metrics. They instrument various components,
see [Spark_dropwizard_metrics_info](Spark_dropwizard_metrics_info.md)
 and can sink to a variety of endpoints, see [Spark monitoring documentation](https://spark.apache.org/docs/latest/monitoring.html)
This document details how to configure Spark to sink metrics to a graphite endpoint.
It has been developed and tested in the context of building a dashboard with InfluxDB (acting as
the graphite endpoint) and grafana for visualization.
There are multiple to configure metrics sink in Spark. One way is to explicitly set the relevant 
configuration parameters. Another method is about using the metrics.properties file.

## Spark configuration parameters to sink metrics

This is an example of to configure the Spark metrics system to sink to a graphite endpoint using 
Spark configuration parameters. There are many options t set parameters in Spark, refer to doc,
this is an example with spark-submit:
  ```
  spark-submit/spark-shell/pyspark
  --conf "spark.metrics.conf.*.sink.graphite.class"="org.apache.spark.metrics.sink.GraphiteSink" \
  --conf "spark.metrics.conf.*.sink.graphite.host"="graphiteEndPoint_influxDB_hostName>" \
  --conf "spark.metrics.conf.*.sink.graphite.port"=<graphite_listening_port> \
  --conf "spark.metrics.conf.*.sink.graphite.period"=10 \
  --conf "spark.metrics.conf.*.sink.graphite.unit"=seconds \
  --conf "spark.metrics.conf.*.sink.graphite.prefix"="lucatest" \
  --conf "spark.metrics.conf.*.source.jvm.class"="org.apache.spark.metrics.source.JvmSource" \
  ```
**Notes:** 
  - the '*' in the parameters names indicate that you want to trace all 
  available components (e.g. driver, executor, etc).   
  - You can limit tracing to selected components of interest by listing the component name 
  at the place of '*' in the example.
  - Another option to deploy Spark configuration parameters is to add them to 
  `$SPARK_CONF_DIR/spark-defaults.conf`
  - Setting `spark.metrics.conf.*.source.jvm.class` is optional

**Additional configuration parameters:**
  - streaming metrics, relevant for streaming queries: `--conf spark.sql.streaming.metricsEnabled= true`
  - appStatus metrics, introduced in Spark 3.0 `--conf spark.app.status.metrics.enabled=true`

## Configure metrics sink using the metrics properties file

Spark metrics can be configured using a metrics properties file, byt default located in 
`$SPARK_CONF_DIR/metrics.properties`.
This is an example of metrics.properties to configure a graphite sink:
  ```
  *.sink.graphite.class=org.apache.spark.metrics.sink.GraphiteSink
  *.sink.graphite.host=<raphiteEndPoint_influxDB_hostName>
  *.sink.graphite.port=<listening_port> # must match influxDB configuration file
  *.sink.graphite.period=10   # Configurable
  *.sink.graphite.unit=seconds
  *.sink.graphite.prefix=lucatest # Optional value/label
  *.source.jvm.class=org.apache.spark.metrics.source.JvmSource # Optional JVM metrics
  ```

**Notes:**
  - If you are using the option of using metrics.properties file, and running Spark on YARN, 
  put metrics.properties in SPARK_CONF_DIR, it will be used by the driver and shipped
  to the executors containers where the config will be read by the containers.
  - You can also distribute the metrics properties file in a location different than the default.  
    In that case you should set the parameter `--conf spark.metrics.conf=<PATH_to_metrics.properties>`
    and use a path that can be resolved by all the components you want to sink  metrics from
    (for example driver, executor, etc). For example this can be facilitated by using a shared 
    filesystem or by distributing copies of the metrics file 
  - If you are using YARN --files metrics.properties will ship the file to the home directory 
    of the executors containers.
