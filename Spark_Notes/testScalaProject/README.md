# testSparkScala

This is example code of how you can use Spark from Scala code. 
It is a basic working project, just to show how to get started.

How to run a test:
```
# build the jar
sbt clean package

bin/spark-submit --class ch.cern.test.testSparkScala <path>/target/scala-2.11/testsparkscala_2.11-0.1.jar
```
