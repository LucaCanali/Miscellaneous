# testSparkScala

This is example code of how you can use Apache Spark from Scala applications.
This uses sbt to build the project.

How to run a test:
```
# build the jar
sbt +clean +package

// scala 2.12
bin/spark-submit --class ch.cern.test.testSparkScala <path>/target/scala-2.12/testsparkscala_2.12-0.1.jar

// scala 2.13
bin/spark-submit --class ch.cern.test.testSparkScala <path>/target/scala-2.13/testsparkscala_2.13-0.1.jar
```
