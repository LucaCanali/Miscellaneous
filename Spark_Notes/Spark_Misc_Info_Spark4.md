# Miscellaneous Spark commands and API in Apache Spark 4.x

---
Bind variables in SQL (Spark 4.x)

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
SQL variables (Spark 4.x)

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


