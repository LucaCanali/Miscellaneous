# Apache Spark for High Energy Physics
In this page you can find links and examples related to using Spark for reading and processing HEP data.

--- 
### Dimuon mass spectrum and histogram calculation using CERN opendata
  * [Dimuon mass spectrum and histogram](Dimuon_mass_spectrum_histogram_Spark_mapInArrow.ipynb) notebook (small scale)
  * [Dimuon mass spectrum and histogram at SCALE](Dimuon_mass_spectrum_histogram_Spark_mapInArrow_SCALE.ipynb) notebook (200 cores and 200 GB of data)
  * [Dimuon mass spectrum and histogram using Array of Struct](Use_ArrayOfStruct__Dimuon_mass_spectrum_histogram_Spark_mapInArrow.ipynb) notebook. Minor variation, small scale.

### LHCb Open Data Analysis Using PySpark
 * **Jupyter notebook on GitHub at: [LHCb_OpenData_Spark.ipynb](LHCb_OpenData_Spark.ipynb)**  
 * [CERN SWAN service](https://swan.web.cern.ch) users, run from [this link to CERN Box](https://cernbox.cern.ch/index.php/s/98RK9xIU1s9Lf08)
   
### CMS Big Data project
 * Example notebook using CMS opendata, spark-root and Hadoop-XRootD: [CMS_BigData_Opendata_Spark_Example1.ipynb](CMS_BigData_Opendata_Spark_Example1.ipynb)
---
Relevant technology and links:
 * [spark-root/laurelin](https://github.com/spark-root/laurelin) a library to read HEP files in ROOT format into Spark DataFrames.
 * Now obsolete: [spark-root](https://github.com/diana-hep/spark-root): a library to read HEP files in ROOT format into Spark DataFrames.
 * [Spark SQL, DataFrames and Datasets Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
 * [CERN Open Data portal](http://opendata.cern.ch/)
 * [LHCb Open Data project](https://github.com/lhcb/opendata-project)
 * [CERN SWAN service](https://swan.web.cern.ch)
 * [CMS Big Data project](https://cms-big-data.github.io)
 * [Hadoop-XRootD connector](https://gitlab.cern.ch/awg/hadoop-xrootd-connector) - allows to read files from EOS using the XRootD protocol (currently available on CERN Gitlab, will be available on GitHub)
 