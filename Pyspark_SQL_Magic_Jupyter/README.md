# IPython/Jupyter magic functions for running Spark SQL using Pyspark

This folder is about a simple implementation with examples of IPython/Jupyter %sql "magic functions" for pyspark. These can be used as shortcuts for running SQL with Spark when using Python notebooks.

- Example notebook: [**IPython_Pyspark_SQL_Magic.ipynb**](IPython_Pyspark_SQL_Magic.ipynb)
- Code: [**IPython_Pyspark_SQL_Magic.py**](IPython_Pyspark_SQL_Magic.py)

**Blog entry:** http://externaltable.blogspot.com/2016/11/ipythonjupyter-sql-magic-functions-for.html

```
Usage: %<magic> for line magic or %%<magic> for cell magic.
Example sql magic functions:

%sql <statement>          - return a Spark DataFrame for lazy evaluation of the SQL
%sql_show <statement>     - run the SQL statement and show max_show_lines (50) lines 
%sql_display <statement>  - run the SQL statement and display unsing an HTML table. This is implemented unsing Pandas and displays max_show_lines (50)
%sql_explain <statement>  - display the execution plan of the SQL statement
```

