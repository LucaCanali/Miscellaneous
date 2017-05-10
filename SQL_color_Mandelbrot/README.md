# SQL with color

The terminal graphics is taken from the code of [OraLatencyMap](../../OraLatencyMap) and [PyLatencyMap](../../PyLatencyMap)
The example with the Mandelbrot set in SQL is a port to Oracle (SQL*plus) from a PostgreSQL version (see references).   

**See also the blog entry: http://externaltable.blogspot.com/2015/08/add-color-to-your-sql.html**

Example SQL for displaying color palettes:
- [Color_palette_blue.sql](Color_palette_blue.sql)
- [Color_palette_yellow-red.sql](Color_palette_yellow-red.sql)

Mandelbrot set in SQL, Oracle version:
- [Mandelbrot_SQL_Oracle_text.sql](Mandelbrot_SQL_Oracle_text.sql) (text version, no color)
- [Mandelbrot_SQL_Oracle_color_blue.sql](Mandelbrot_SQL_Oracle_color_blue.sql)
- [Mandelbrot_SQL_Oracle_color_yellow-red.sql](Mandelbrot_SQL_Oracle_color_yellow-red.sql)

PostgreSQL version:
- [Mandelbrot_SQL_PostgreSQL_color_blue.sql](Mandelbrot_SQL_PostgreSQL_color_blue.sql)

Spark SQL version:
- [Spark_SQL_UDF_examples_Mandelbrot](Miscellaneous/Spark_Notes/Spark_SQL_UDF_examples_Mandelbrot)

# Eye candy

![Mandelbrot SQL in color](http://2.bp.blogspot.com/-VEqSBLulncs/VeNd4ztamuI/AAAAAAAAEuQ/JC608pPcPqk/s1600/Mandelbrot_SQL_collage.png)
   
   
![Mandelbrot SQL in color](Miscellaneous/Spark_Notes/Spark_SQL_UDF_examples_Mandelbrot/Spark_SQL_UDF_example_Mandelbrot_Images.png)

## References:
- https://en.wikipedia.org/wiki/Mandelbrot_set
- https://wiki.postgresql.org/wiki/Mandelbrot_set
- http://thedailywtf.com/articles/Stupid-Coding-Tricks-The-TSQL-Madlebrot
- https://www.sqlite.org/lang_with.html
- https://community.oracle.com/message/3136057
- http://xoph.co/20130917/mandelbrot-sql/

Author: @LucaCanaliDB, August 2015
