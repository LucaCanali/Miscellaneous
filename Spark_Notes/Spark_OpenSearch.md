## Notes on using Apache Spark with OpenSearch

These are notes and examples of how to use Spark with [OpenSearch](https://github.com/opensearch-project) with examples tested using the CERN OpenSearch service.  
Version details: OpenSearch v2.2.1, Spark version 3.3.1, opensearch-hadoop library (built from GitHub main, Jan 2023)

## Where to find the code and documentation
- [OpenSearch](https://github.com/opensearch-project) is a community driven project which has started as a fork
of [Elasticsearch and Kibana](https://www.elastic.co/).  
- Elasticsearch client libraries cannot be used with OpenSearch
  - When migrating Spark clients from Elasticsearch to OpenSearch the changes could be minor,
    as the two APIs are similar, but require developers' attention.
- The OpenSearch client library for Spark is: https://github.com/opensearch-project/opensearch-hadoop
- Documentation: 
  - see the [opensearch-hadoop README](https://github.com/opensearch-project/opensearch-hadoop#readme)
  - Elastic has a more detailed description, although beware of the different API naming at:
    [elastic and Spark](https://www.elastic.co/guide/en/elasticsearch/hadoop/current/spark.html) 

## How to build the Spark libraries/jars for OpenSearch
See the official releases on GitHub, for example:
  - https://github.com/opensearch-project/opensearch-hadoop/releases/tag/v1.0.0

Example of how to build from the GitHub repo:
```
git clone https://github.com/opensearch-project/opensearch-hadoop
cd opensearch-hadoop

# the project is built with gradle 
# note, it needs java11 to build
# it also needs to have JAVA 8 
export JAVA8_HOME=/usr/lib/jvm/java-1.8.0-openjdk

# build with gradle
./gradlew opensearch-spark-30:build
```

In my tests the gradle build throws errors, but it is still useful as it manages to build the
jars needed for using Spark with OpenSearch:
```
spark/core/build/libs/opensearch-spark_2.12-3.0.0-SNAPSHOT-spark30scala212.jar
spark/sql-30/build/libs/opensearch-spark-30_2.12-3.0.0-SNAPSHOT.jar
thirdparty/build/libs/thirdparty-3.0.0-SNAPSHOT-all.jar
```

## Apache Spark and OpenSearch

### JARs and configurations

Currently (Jan 2023), there are no published maven-central  packages for OpenSearch-Hadoop client libraries, 
see above paragraph on how to build the project from source.   
Note see also the paragraph below "How to create and configure OpenSearch at CERN"  
This is an example of how I used spark-shell with OpenSearch:

```
# Edit the JARs path with your local build
# Stopgap: I have uploaded the jars on a personal website
JAR1=http://canali.web.cern.ch/res/opensearch-spark_2.12-3.0.0-SNAPSHOT-spark30scala212.jar
JAR2=http://canali.web.cern.ch/res/opensearch-spark-30_2.12-3.0.0-SNAPSHOT.jar
JAR3=http://canali.web.cern.ch/res/thirdparty-3.0.0-SNAPSHOT-all.jar

# Edit with the OpenSearch endpoint
OPENSEARCH_URL="https://es-testspark1.cern.ch:443"

# Edit with the authentication credentials
# for OpenSearch basic authentication, 
# see below with details on how to create the user and granting the privilges
USERNAME="test1" 
PASS="..."

bin/spark-shell --master local[*] \
--jars $JAR1,$JAR2,$JAR3 \
--conf spark.opensearch.nodes= $OPENSEARCH_URL \
--conf spark.opensearch.nodes.path.prefix="/es" \
--conf spark.opensearch.nodes.wan.only=true \
--conf spark.opensearch.net.http.auth.user=$USERNAME \
--conf spark.opensearch.net.http.auth.pass=$PASS
```

### Additional configuration parameters

Several configuration parameters are available.
Currently, the best documentation on this is in the elastic website at
[elastic configurations](https://www.elastic.co/guide/en/elasticsearch/hadoop/current/configuration.html)]  
Replace `es.` with `opensearch.` prefix when using OpenSearch. 

OpenSearch configuration parameters can be set via Spark configuration by adding the additional prefix `spark.` to the
configuration parameters, as in this example:
`--conf spark.opensearch.nodes= $OPENSEARCH_URL`

OpenSearch configuration can also be specified via options with the Spark DataFrame reader/writer, as in this example:
```
spark.read.format("opensearch")
 .option("opensearch.net.http.auth.user","test1")
 .option("opensearch.net.http.auth.pass","mypass")
 .load("spark_docs1").show()
```

### How to write a Spark DataFrame into OpenSearch

From spark-shell (see paragraph above on how to start it with jars and configuration):
```
// Create dummy test data in a Spark DataFame
val df=spark.sql("select id, 'aaaa' payload from range(10)")

// This writes using OpenSearch Spark sql extensions
import org.opensearch.spark.sql._  
df.saveToOpenSearch("spark_docs1")

// Another way to write (append) into OpenSearch is by using the Spark Dataframe Writer API 
df.write.format("opensearch").mode("append").save("spark_docs1")

// this will overwrite existing data
// df.write.format("opensearch").mode("overwrite").save("spark_docs1")
```

### How to read from OpenSearch into a Spark DataFrame

```
// Read using the OpenSearch sql extensions
import org.opensearch.spark.sql._
spark.esDF("spark_docs1").show()

// Read using the Spark DataFrame reader API
spark.read.format("opensearch").load("spark_docs1").show()
```

### Spark filter operations running on OpenSearch
 
A key point about using OpenSearch is about indexing data, 
so queries that have filter operations (as opposed to retrieving all data) 
are very important in this context.  

The OpenSearch-Hadoop connector will push down filter conditions by default.  
Spark will also apply the filter on the result by default.    
OpenSearch configurations can be used to change those behaviors.   
Examples:

```
// These filters will be pushed down to OpenSearch 
spark.read.format("opensearch").load("spark_docs1").filter("id==2").show()
spark.read.format("opensearch").load("spark_docs3").filter("payload like '%2'").show()

// Ad-hoc filtering syntax 
import org.opensearch.spark.sql._
spark.esDF("spark_docs1", "?q=id:2").show()
```

Notes:
- these Spark DataFrame reader options can be used to change the defaults regarding pushdown:
```
option("double.filtering", "false")
option("pushdown", "false")
```
-You can see the effect on the Spark WebUI in the DataFrame/SQL tab, when pushdown is not used, all rows are returned
to Spark when the filter is applied, as opposed to returning only the rows that pass the filter in OpenSearch.
-More details on pushdown filters at:
https://www.elastic.co/guide/en/elasticsearch/hadoop/current/spark.html#spark-pushdown

### Pyspark and Spark SQL

PySpark can be used in a similar way as with the Scala examples above:
```
# Python example with PySpark
bin/pyspark --master local[*] \
--jars $JAR1,$JAR2,$JAR3 \
--conf spark.opensearch.nodes= $OPENSEARCH_URL \
--conf spark.opensearch.nodes.path.prefix="/es" \
--conf spark.opensearch.nodes.wan.only=true \
--conf spark.opensearch.net.http.auth.user=$USERNAME \
--conf spark.opensearch.net.http.auth.pass=$PASS

# Write into OpenSearch using the Spark Dataframe Writer API 
df.write.format("opensearch").mode("append").save("spark_docs1")

# Read using the Spark DataFrame reader API
spark.read.format("opensearch").load("spark_docs1").show()

# The filter will be pushed down to OpenSearch 
spark.read.format("opensearch").load("spark_docs1").filter("id==2").show()
```

Spark SQL can be used for DataFrame operations, as usual in Spark:
```
df=spark.read.format("opensearch").load("spark_docs1")
df.createOrReplaceTempView("t1")

# Select with predicate pushdown into OpenSearch
spark.sql("select * from t1 where id=2").show()
```

### Spark RDD API to OpenSearch
Spark DataFrame API and Spark SQL are the more common API with Spark, however they are suitable for structured
data (data with a schema).  
Spark RDD is the low-level API in Spark, and it can handle more complex (non-structured) data. 
This is how you can use OpenSearch with the Spark RDD API:

````
// run spark-shell as detailed in the paragraph above
import org.opensearch.spark._

// define a case classes
case class NumberEnglish(num: Integer, english: String)
case class NumberEnglishFrench(num: Integer, english: String, french: String)              

// generate non-structured test data in a rdd
val one = NumberEnglish(1, "one")
val two = NumberEnglish(2, "two")
val thmree = NumberEnglishFrench(3, "three", "trois")
val rdd = sc.makeRDD(Seq(one, two, three))             

rdd.saveToOpenSearch("spark_docs2")
````

## How to create and configure OpenSearch at CERN
- Request the creation of an OpenSearch instance
  - open a ticket using ServiceNow 

- To use basic authentication you need to create a username and password and give the necessary grants:
- From the OpenSearch dashboard navigate to "Internal users" and clink on "create internal user and assign role"
- Add the necessary role to the user, for testing grant "all_access"
- Note, as stated in the documentation "ensure that the role all_access is mapped directly to the internal user and not a backend role."
