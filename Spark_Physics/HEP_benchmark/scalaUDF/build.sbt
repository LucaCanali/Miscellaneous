name := "scalaUDF"

version := "0.1"

scalaVersion := "2.12.18"

crossScalaVersions := Seq("2.12.18", "2.13.8")

libraryDependencies += "org.apache.spark" %% "spark-sql" % "3.5.1"
libraryDependencies += "net.jafama" % "jafama" % "2.3.2"
