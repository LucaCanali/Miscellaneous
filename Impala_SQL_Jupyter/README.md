# Jupyter/IPython notebooks for querying Apache Impala

Author: Luca.Canali@cern.ch, April 2016

**Blog entry: http://externaltable.blogspot.com/2016/04/ipython-notebooks-for-querying-apache.html**

---
**Example notebooks:**
- [**Impala_Basic.ipynb**](Impala_Basic.ipynb) - basic example, SQL on Impala using Cloudera's impyla 
- [**Impala_SQL_Magic.ipynb**](Impala_SQL_Magic.ipynb) - SQL on Impala, better user interface using 'SQL magic'
- [**Impala_Basic_Kerberos.ipynb**](Impala_Basic_Kerberos.ipynb) - basic example, SQL on Impala using Cloudera's impyla. With Kerberos authentication. 
- [**Impala_SQL_Magic_Kerberos.ipynb**](Impala_SQL_Magic_Kerberos.ipynb) - SQL on Impala, better user interface using 'SQL magic'. With Kerberos authentication.

---
**Dependencies and pointers on how to build a test environemnt:**
- Set up Jupyter/IPython: download and install [Anaconda](https://www.continuum.io/downloads) from Continuum Analytics)
- Install [Cloudera impyla](https://github.com/cloudera/impyla) for example with `pip install impyla`
- Install ipython-sql from <https://github.com/LucaCanali/ipython-sql>
- Additional steps for Kerberos:
    - `yum install cyrus-sasl-devel`
    - `yum install gcc-c++`
    - `pip install thrift_sasl`


