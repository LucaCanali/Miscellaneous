name := "sparkHistogram"

version := "0.1"

licenses += ("Apache-2.0", url("http://www.apache.org/licenses/LICENSE-2.0"))

description := "sparkHistogram is a tool to generate histograms use the Apache Spark DataFrame API."
developers := List(Developer(
  "LucaCanali", "Luca Canali", "Luca.Canali@cern.ch",
  url("https://github.com/LucaCanali")
))
homepage := Some(url("https://github.com/LucaCanali/Miscellaneous/tree/master/Spark_Notes/Spark_Histograms"))


scalaVersion := "2.12.17"

libraryDependencies += "org.apache.spark" %% "spark-sql" % "3.4.0"
