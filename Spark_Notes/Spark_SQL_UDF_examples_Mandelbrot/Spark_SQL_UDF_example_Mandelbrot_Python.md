## Examples of Apache Spark SQL with user defined functions

To provide an original example this computes and displays the Mandelbrot set using Spark SQL, 
the output uses ASCII graphics and there is also a version with ANSI code colors.  
Tested on Spark 2.0 and 2.1  
Author: @LucaCanaliDB, January 2017  
How to run: 
* Copy-paste the code for UDF and SQL into a Spark session running with spark-shell or a Scala notebook  
* For the version "SQL with color", use a terminal/notebook that supports ANSI escape codes  

This is the Python version, a Scala version is available at:
[Spark_Notes/Spark_SQL_UDF_example_Mandelbrot](https://github.com/LucaCanali/Miscellaneous/tree/master/Spark_Notes/Spark_SQL_UDF_example_Mandelbrot)
   
## The vanilla ASCII version

**UDF:** This is an helper function, it implements the "Escape time algorithm" for the Mandelbrot set visualization 
as a Spark user defined function.   
Inputs: *cR and cI* represent the point in the set/image to evaluate (c is a complex number).
*maxIterations* is maximum number of iterations.  
Output: the function returns an integer representing the number of iterations to reach the 
"escape point" (|z|^2 = 4) or returns *maxIterations* if it did not reach it.

```python
# the function definition
def mandelbrot(cR, cI, maxIterations):
    zR = cR  
    zI = cI
    i = 1  
    # Iterative formula for Mandelbrot set: z => z^2 + c
    # Escape point: |z|^2 >= 4. Note: z nd c are complex numbers
    while (zR*zR + zI*zI < 4.0 and i < maxIterations):
        newzR = zR*zR - zI*zI +cR
        newzI = 2*zR*zI + cI
        zR = newzR
        zI = newzI
        i += 1
    return i

# registers the function mandelbrot as a UDF for Spark
spark.udf.register("mandelbrot", mandelbrot)
```

**SQL:** Compute and display the Mandelbrot set using ASCII graphics, text version

```python
spark.sql("""
with
    x as (select id, -2.0 + 0.023*cast(id as Float) cR from range(0,110)),
    y as (select id, -1.1 + 0.045*cast(id as Float) cI from range(0,50))
select translate(cast(collect_list(substring(' .:::-----++++%%%%@@@@#### ',
       mandelbrot(x.cR, y.cI, 27), 1)) as string), ',', '') as Mandelbrot_Set
from y cross join x 
group by y.id 
order by y.id desc""").show(200, False)
```
   
      
## The SQL color version

This computes and displays the Mandelbrot set on the terminal using color, with a blue palette   
Note: it requires a terminal or notebook with support for ANSI escape codes

```python
result = spark.sql("""
with
    x as (select id, -2.0 + 0.023*cast(id as Float) cR from range(0,110)),
    y as (select id, -1.1 + 0.045*cast(id as Float) cI from range(0,50))
select translate(cast(collect_list(color) as String), ',' , '') as value
from y cross join x cross join values 
     (0, concat('\u001B','[48;5;0m ','\u001B','[0m')),  -- Black
     (1, concat('\u001B','[48;5;15m ','\u001B','[0m')), -- White
     (2, concat('\u001B','[48;5;51m ','\u001B','[0m')), -- Light blue
     (3, concat('\u001B','[48;5;45m ','\u001B','[0m')), 
     (4, concat('\u001B','[48;5;39m ','\u001B','[0m')),
     (5, concat('\u001B','[48;5;33m ','\u001B','[0m')),
     (6, concat('\u001B','[48;5;27m ','\u001B','[0m')), 
     (7, concat('\u001B','[48;5;21m ','\u001B','[0m'))  -- Dark blue
     as palette(id, color)
where  cast(substring('012223333344445555666677770', mandelbrot(x.cR, y.cI, 27), 1) as Int) = palette.id
group by y.id 
order by y.id desc""").collect()

# print out the result set of the query line by line
for line in result:
    print(line[0])
```


This computes and displays the Mandelbrot set on the terminal using color, with a yellow-red palette   
Note: it requires a terminal or notebook with support for ANSI escape codes

```python
result = spark.sql("""
with
    x as (select id, -2.0 + 0.023*cast(id as Float) cR from range(0,110)),
    y as (select id, -1.1 + 0.045*cast(id as Float) cI from range(0,50))
select translate(cast(collect_list(color) as String), ',' , '') as value
from y cross join x cross join values 
     (0, concat('\u001B','[48;5;0m ','\u001B','[0m')),  -- Black
     (1, concat('\u001B','[48;5;15m ','\u001B','[0m')), -- White
     (2, concat('\u001B','[48;5;226m ','\u001B','[0m')),
     (3, concat('\u001B','[48;5;220m ','\u001B','[0m')),
     (4, concat('\u001B','[48;5;214m ','\u001B','[0m')),
     (5, concat('\u001B','[48;5;208m ','\u001B','[0m')),
     (6, concat('\u001B','[48;5;202m ','\u001B','[0m')),
     (7, concat('\u001B','[48;5;1961m ','\u001B','[0m'))
     as palette(id, color)
where  cast(substring('012223333344445555666677770', mandelbrot(x.cR, y.cI, 27), 1) as Int) = palette.id
group by y.id 
order by y.id desc""").collect()

# print out the result set of the query line by line
for line in result:
    print(line[0])
```



