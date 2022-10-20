# testSparkScala

This is example code of how you can use Apache Spark from Scala applications.
This uses sbt to build the project.

How to run a test:
```
# build the jar
sbt clean package

bin/spark-submit --class ch.cern.test.testSparkScala <path>/target/scala-2.12/testsparkscala_2.12-0.1.jar
```
