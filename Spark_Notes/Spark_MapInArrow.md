# MapInArrow

These are working notes about the mapInArrow functionality introduced in [SPARK-37227](https://issues.apache.org/jira/browse/SPARK-37227)
and the related PR [#34505](https://github.com/apache/spark/pull/34505)

- The main idea about this is that bypassing the conversion to Pandas can improve the performance, in particular
when dealing with arrays and complex datatypes where Pandas conversion introduces a performance penalty

- Libraries other than Pandas can be used for data processing in the (vectorized) UDF
  - The [Awkward array library](https://awkward-array.readthedocs.io/en/latest/index.html) is used instead of Pandas to handle data processing for the tests reported here.  

- The tests reported here, detail a 4x speedup on a particular use case: squaring numerical arrays

**Limitations and other discussions:**
- mapInArrow needs to serialize and deserialize all the columns of the DataFrame,
which could add an overhead if you need to process just a few columns
- mapInArrow data needs to folloe the DataFrame schema. You need to take care of adding the 
input and output columns with their datatypes to the schema
- See also discussion in PR [#26783](https://github.com/apache/spark/pull/26783) on a previous test proposal
for extended Spark Arrow UDF

## Some basic performance tests comparing MapInArrow and MapInPandas

See code below, or see:
  * Tests  in a notebook with [tests mapInArrow](Tests_mapInArrow.ipynb) 

Other examples:
  * Jupyter notebook [Dimuon mass spectrum and histogram](Dimuon_mass_spectrum_histogram_Spark_mapInArrow.ipynb)
  * Jupyter notebook [Dimuon mass spectrum and histogram using Array of Struct](Use_ArrayOfStruct__Dimuon_mass_spectrum_histogram_Spark_mapInArrow.ipynb)

----

### Test setup:
 - Spark 3.3.0-SNAPSHOT (compiled from Spark master at the time of these tests) 
 - `pyspark --master local[1]` -> we use only one core to reduce measurement noise and focus on the UDF execution
 - requires: `pip install pyarrow` and `pip install awkward`
 - We use arrays in the test dataframes, as this is where we find the biggest difference between mapInPandas and mapInArrow
 
### Tests, reference operations without UDFs

 - Test reference (dummy operation) 1:
   - just write a test DataFrame produced on-the-gly to the "noop" data sink (data is processed, but nothing is written)  
   - Run time: ~5 sec
   - Code:
```
bin/pyspark --master local[1]

sc.setLogLevel('WARN')
import time

df = sql("select Array(rand(),rand(),rand()) col3 from range(1e8)")

start = time.time()

df.write.format("noop").mode("overwrite").save()

end= time.time()
print(f"Run time: {round(end-start,1)}")
```

- Test reference (squared arrays with higher order functions) 2:
  - this performs the square of an array column using higher order function, therefore working in the JVM
  - Run time: ~ 18 sec
  - Code:
```
df = sql("select Array(rand(),rand(),rand()) col3 from range(1e8)")

df2 = df.transform(lambda x: x * x)
df2.show(2,False)

# SQL version
# df.createOrReplaceTempView("t1")
# df2 = spark.sql("SELECT transform(col3, t -> t*t) as col3_squared FROM t1")

start = time.time()

df2.write.format("noop").mode("overwrite").save()

end= time.time()
print(f"Run time: {round(end-start,1)}")

```

### Tests using MapInPandas

- Test_Pandas 1 (dummy UDF): 
  - Just a dummy UDF that just serializes data, converts to Pandas and deserializes back using mapInPandas
  - Note we use a test DataFrame that contains an array 
  - Run time: ~47 sec
```
import time

df = sql("select Array(rand(),rand(),rand()) col3 from range(1e8)")

# A dummy UDF that just returns the input data
def UDF_test_func(iterator):
    for batch in iterator:
        yield batch

start = time.time()

df.mapInPandas(UDF_test_func, df.schema).write.format("noop").mode("overwrite").save()

end= time.time()
print(f"Run time: {round(end-start,1)}")

```
- Test_Pandas 2 (compute the square of arrays):
   - a UDF that squares the input data using Pandas serialization
   - run time: ~ 100 sec
```
import time

df = sql("select Array(rand(),rand(),rand()) col3 from range(1e8)")

# UDF function that squares the input
def UDF_test_func(iterator):
    for batch in iterator:
        yield batch*batch

start = time.time()

df.mapInPandas(UDF_test_func, df.schema).write.format("noop").mode("overwrite").save()

end= time.time()
print(f"Run time: {round(end-start,1)}")
```

### Target: testing with MapInArrow

- Test_Arrow 1 (dummy UDF):
  - A dummy UDF as in Test_Pandas 1, but this time using mapInArrow, so skipping conversion to Pandas
  - Run time: ~ 20 sec
  - Code:
    - The code is the same as in Test_Pandas 1 with the change `mapInPandas` -> `mapInArrow`

- Test_Arrow 1b (dummy UDF with awkward array library):
  - Again a dummy UDF, this time we add serialization and deserialization to awkward array
  - Run time: ~ 21 sec
  - Code:
```
import awkward as ak
import time

df = sql("select Array(rand(),rand(),rand()) col3 from range(1e8)")

# a dummy UDF that convert back and forth to awkward arrays
# it just returns the input data
def UDF_test_func(iterator):
    for batch in iterator:
        b = ak.from_arrow(batch)
        yield from ak.to_arrow_table(b).to_batches()


start = time.time()

df.mapInArrow(UDF_test_func, df.schema).write.format("noop").mode("overwrite").save()

end= time.time()
print(f"Run time: {round(end-start,1)}")

```

- Test_Arrow 2 (compute the square of arrays with awkward arrays library):
  - This computes the square of arrays, as in Test_Pandas 2, but this time with arrow serialization + awkward array library
  - Run time: ~ 23 sec
  - Code:
```
sc.setLogLevel('WARN')

import awkward as ak
import numpy as np
import time

df = sql("select Array(rand(),rand(),rand()) col3 from range(1e8)")

# process using the awkward arrays library
def UDF_test_func(iterator):
    for batch in iterator:
        b = ak.from_arrow(batch)
        b2 = ak.zip({"col3": np.square(b["col3"])}, depth_limit=1)
        yield from ak.to_arrow_table(b2).to_batches()

start = time.time()

df.mapInArrow(UDF_test_func, df.schema).write.format("noop").mode("overwrite").save()

end= time.time()
print(f"Run time: {round(end-start,1)}")

```

---
