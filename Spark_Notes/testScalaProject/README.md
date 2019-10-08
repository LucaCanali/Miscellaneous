# Test Spark with Scala Code

This is example code of how you can use Spark from Scala code. 
It is a basic working project, just to show how to get started.

How to run a test:
- prerequisite, install sbt, download from from https://www.scala-sbt.org version 0.13.18
  - note, the first time you build with sbt it will download several packages and therefore will be slow   
```
# build the jar
sbt clean package

# test with Spark
bin/spark-submit --class ch.cern.test.testSparkScala <path>/target/scala-2.11/testsparkscala_2.11-0.1.jar
```
