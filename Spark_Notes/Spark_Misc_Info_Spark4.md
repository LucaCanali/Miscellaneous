# Miscellaneous Spark commands and API in Apache Spark 4.x
This briefly shows examples of new features and commands in Spark 4.x

---
## Bind variables in SQL (Spark 4.x)

Introduced in Spark 4.0.0, this feature supports bind variables in SQL queries.

```
spark.sql("execute immediate 'select :text' using('Hello World!' as text)").show()
+------------+
|        text|
+------------+
|Hello World!|
+------------+
```
---
## SQL variables (Spark 4.x)

Introduced in Spark 4.0.0, this feature supports variable substitution in SQL queries.

```
spark.sql("declare mytext='Hello World!'")
spark.sql("select mytext").show()
+------------+
|      mytext|
+------------+
|Hello World!|
+------------+

spark.sql("DECLARE OR REPLACE VARIABLE myvar INT DEFAULT 42;")
spark.sql("select myvar").show()
+-----+
|myvar|
+-----+
|   42|
+-----+

spark.sql("SET VAR myvar = 12")
spark.sql("select myvar").show()
+-----+
|myvar|
+-----+
|   12|
+-----+

spark.sql("DECLARE mysqltext STRING")
spark.sql("SET VAR mysqltext = 'select 42'")
spark.sql("execute immediate mysqltext").show()
+---+
| 42|
+---+
| 42|
+---+
```
---
## SQL functions
Allows to create functions in the catalog and use them in SQL

```
spark.sql("""
CREATE OR REPLACE FUNCTION testSQL2(id INT) RETURNS TABLE(a INT, b INT)
RETURN SELECT 1, id+1
""")
```

----
## Pyarrow in Pyspark  
User-defined table functions (UDTF)  
Python data source API  

See: https://spark.apache.org/docs/latest/api/python/tutorial/sql/index.html

Snippet of UDTF from the documenation:
```
from pyspark.sql.functions import lit, udtf

# Define a UDTF using the `udtf` decorator directly on the class.
@udtf(returnType="num: int, squared: int")
class SquareNumbers:
    def eval(self, start: int, end: int):
        for num in range(start, end + 1):
            yield (num, num * num)

# Invoke the UDTF in PySpark using the SquareNumbers class directly.
SquareNumbers(lit(1), lit(3)).show()
```
----
## Variant

Variant is a new datatype introduced in Spark 4. It's intended to store and operate with semi-structured data in an optimized way (e.g. faster than using JSON).

```
from datetime import date, datetime
from decimal import Decimal
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType

from pyspark.sql.functions import try_parse_json, try_variant_get, col

# Sample JSON data
data = [
    '1234567890123456789',
    '12345.6789',
    '"Hello, World!"',
    'true',
    '{"id": 1, "attributes": {"key1": "value1", "key2": "value2"}}',
    '{"id": 2, "attributes": {"key1": "value3", "key2": "value4"}}',
]

# Load data into DataFrame with VARIANT
df = spark.createDataFrame(data, StringType()).select(try_parse_json(col("value")).alias("variant_data"))
df.printSchema()
df.show(truncate=False)

root
 |-- variant_data: variant (nullable = true)

+-------------------------------------------------------+
|variant_data                                           |
+-------------------------------------------------------+
|1234567890123456789                                    |
|12345.6789                                             |
|"Hello, World!"                                        |
|true                                                   |
|{"attributes":{"key1":"value1","key2":"value2"},"id":1}|
|{"attributes":{"key1":"value3","key2":"value4"},"id":2}|
+-------------------------------------------------------+
```

```
# Accessing elements inside the VARIANT
df.select(
    try_variant_get(col("variant_data"), "$", "long").alias("long_value"),
    try_variant_get(col("variant_data"), "$.id", "int").alias("id"),
    try_variant_get(col("variant_data"), "$.attributes.key1", "string").alias("key1"),
    try_variant_get(col("variant_data"), "$.attributes.key2", "string").alias("key2"),
).show()

# Accessing elements inside the VARIANT
df.select(
    try_variant_get(col("variant_data"), "$", "long").alias("long_value"),
    try_variant_get(col("variant_data"), "$.id", "int").alias("id"),
    try_variant_get(col("variant_data"), "$.attributes.key1", "string").alias("key1"),
    try_variant_get(col("variant_data"), "$.attributes.key2", "string").alias("key2"),
).show()
```
---
## Profiling UDF
```
import io
from contextlib import redirect_stdout

from pyspark.sql.functions import pandas_udf

df = spark.range(10)
@pandas_udf("long")
def add1(x):
    return x + 1

added = df.select(add1("id"))

spark.conf.set("spark.sql.pyspark.udf.profiler", "perf")
spark.profile.clear()
added.collect()

# Only show top 10 lines
output = io.StringIO()
with redirect_stdout(output):
    spark.profile.show(type="perf")

print("\n".join(output.getvalue().split("\n")[0:20]))
```
---
## SQL pipe syntax

Spark 4 support the SQl pipe syntax, see also: https://spark.apache.org/docs/latest/sql-pipe-syntax.html
Example from Spark doc:
```
spark.sql("""
VALUES ('apples', 3), ('bananas', 4) t(item, sales)
|> AS produce_sales
|> LEFT JOIN
     (SELECT "apples" AS item, 123 AS id) AS produce_data
     USING (item)
|> SELECT produce_sales.item, sales, id""").show()
```
---
## Recursive CTE
Spark 4.1 introduces support for recursive common table expressions
```
spark.sql("""
WITH RECURSIVE t1(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM t1 WHERE n < 5
)
SELECT * from t1""").show()
```
---
## Driver logs
Since Apache Spark 4.0.0, Driver UI provides a way to see driver logs via a new configuration.

`spark.driver.log.localDir=/tmp`

Then, the Spark driver UI can be accessed on http://localhost:4040/logs/. Optionally, the layout of log is configured by the following.

```spark.driver.log.layout="%m%n%ex"```
---
## Spark Kubernetes operator

See details at:
https://apache.github.io/spark-kubernetes-operator/
---

