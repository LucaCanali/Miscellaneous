# MapInArrow

These are working notes about the mapInArrow functionality introduced in [SPARK-37227](https://issues.apache.org/jira/browse/SPARK-37227)
and the related PR [#34505](https://github.com/apache/spark/pull/34505)

- The main idea about this is that bypassing the conversion to Pandas can improve the performance, in particular
when dealing with arrays and complex datatypes where Pandas conversion introduces a performance penalty.

- The [Awkward array library](https://awkward-array.readthedocs.io/en/latest/index.html) is used instead of Pandas to handle data processing.  

Other doc: See also discussion in PR [#26783](https://github.com/apache/spark/pull/26783) on a previous test proposal
for extended Spark Arrow UDF.

## Some basic performance tests comparing MapInArrow and MapInPandas

### Test setup:
 - Spark 3.3.0-SNAPSHOT (compiled from Spark master at the time of these tests) 
 - `pyspark --master local[1]` -> we use only one core to reduce measurement noise and focus on the UDF execution
 - requires: `pip install pyarrow` and `pip install awkward`

 - Test reference 0:
   - just write a test DataFrame produced on-the-gly to the "noop" data sink (data is processed, but nothing is written)  
   - Run time: ~5 sec
   - Code:
```
import time

start = time.time()

df.write.format("noop").mode("overwrite").save()

end= time.time()
print(f"Run time: {round(end-start,1)}")
```

### Reference: testing MapInPandas

- Test_Pandas 1: 
  - Just a dummy UDF that just serializes data, converts to Pandas and deserializes back using mapInPandas
  - Note we use a test DataFrame that contains an array 
  - Run time: ~47 sec
```
sc.setLogLevel('WARN')

from awkward import *
import pyarrow
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
- Test_Pandas 2:
   - a UDF that squares the input data using Pandas serialization
   - run time: ~ 100 sec
```
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

- Test_Arrow 1:
  - A dummy UDF as in Test_Pandas 1, but this time using mapInArrow, so skipping conversion to Pandas
  - Run time: ~ 20 sec
  - Code:
    - The code is the same as in Test_Pandas 1 with the change `mapInPandas` -> `mapInArrow`

- Test_Arrow 1b:
  - Again a dummy UDF, this time we add serialization and deserialization to awkward array
  - Run time: ~ 22 sec
  - Code:
```
# a dummy UDF that convert back and forth to awkward arrays
# it just returns the input data
def UDF_test_func(iterator):
    for batch in iterator:
        b = awkward.from_arrow(batch)
        c = pyarrow.RecordBatch.from_struct_array(awkward.to_arrow(b))
        yield c

start = time.time()

df.mapInArrow(UDF_test_func, df.schema).write.format("noop").mode("overwrite").save()

end= time.time()
print(f"Run time: {round(end-start,1)}")
```
 
