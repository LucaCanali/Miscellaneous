# Jupyter/IPython notebooks for querying Apache Impala

Author: Luca.Canali@cern.ch, April 2016

**Blog entry: http://externaltable.blogspot.com/2016/04/ipython-notebooks-for-querying-apache.html**

---
This folder contains example notebooks on how to use Jupyter/IPython for querying Apache Impala and integrating with Python data analysis and visualization tools.

**Example notebooks:**

| Notebook                   | Short description
| -------------------------- | -------------------------------------------------------------------------------------
| [**Impala_Basic.ipynb**](Impala_Basic.ipynb) | Examples of how to run SQL on Impala using Cloudera's client, impyla.
| [**Impala_SQL_Magic.ipynb**](Impala_SQL_Magic.ipynb) | Examples of how to query Impala using %sql line magic (or %%sql cell magic) and of how to integrate with pandas and visualization with matplotlib. |
| [**Impala_Basic_Kerberos.ipynb**](Impala_Basic_Kerberos.ipynb) | SQL on Impala, with Kerberos authentication.
| [**Impala_SQL_Magic_Kerberos.ipynb**](Impala_SQL_Magic_Kerberos.ipynb) | SQL on Impala with %sql line magic and with Kerberos authentication |

---
**Dependencies and pointers on how to build a test environemnt:**
- Install **IPython and Jupyter**. The following assumes [Anaconda](https://www.continuum.io/downloads) from Continuum Analytics)
- Install **Cloudera impyla** <https://github.com/cloudera/impyla>
    - `pip install impyla`
- Install **ipython-sql**
   - download from <https://github.com/LucaCanali/ipython-sql>
   - `cd ipython-sql` and `(sudo) python setup.py install`
- Additional steps for Kerberos:
    - `yum install cyrus-sasl-devel`
    - `yum install gcc-c++`
    - `pip install thrift_sasl`

