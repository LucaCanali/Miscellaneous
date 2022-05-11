# Jupyter/IPython notebooks for Oracle RDBMS

Author: Luca.Canali@cern.ch, June 2016

**Blog entry:http://externaltable.blogspot.com/2016/06/ipythonjupyter-notebooks-for-oracle.html**

---
This folder contains example notebooks on how to use Jupyter/IPython for querying Oracle databases and integrating with Python data analysis and visualization tools.

**Example notebooks:**

| Notebook                   | Short description
| -------------------------- | -------------------------------------------------------------------------------------|
| [**Oracle_IPython_sqlplus**](Oracle_IPython_sqlplus.ipynb) | Examples of how to use sqlplus inside Jupyter notebooks. It is based on the use of %%bash cell magic and here documents to wrap up sqlplus inside Jupyter cells.|
| [**Oracle_IPython_cx_Oracle_pandas**](Oracle_IPython_cx_Oracle_pandas.ipynb) | Examples of how to query Oracle from Python using cx_Oracle and how to integrate with pandas and visualization with matplotlib.|
| [**Oracle_IPython_SQL_magic**](Oracle_IPython_SQL_magic.ipynb) | Examples of how to query Oracle using %sql line magic (or %%sql cell magic) and the integration with cx_Oracle and pandas.|

---
**Dependencies and pointers to build a test environment:**
- Install **Jupyter notebooks**. For example use [Anaconda](https://www.continuum.io/downloads) Python.
- Install the **Oracle client**
    - Download from https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html
    - When installing the client on a custom directory, also `export LD_LIBRARY_PATH={oracle client home}`
- Check that the Oracle client works and all dependencies are set by running sqlplus from the Oracle client home, example:
    - check client connectivity with: `sqlplus username/password@dbserver:port/service_name`
- Install **cx_Oracle**, for example with `pip install cx_Oracle`
- Install **ipython-sql**, for example with `pip install ipython-sql`

