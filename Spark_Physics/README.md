# Apache Spark for High Energy Physics
  
High Energy Physics (HEP, and also Particle Physics) experiments at the LHC are very data-intensive operations.    
This collects a few simple examples of how Apache Spark can be used in the domain of HEP data analysis.    
See also the blog post [Can High Energy Physics Analysis Profit from Apache Spark APIs?](https://db-blog.web.cern.ch/node/186)  

---
## 1. Dimuon mass spectrum analysis
  
This is a sort of "Hello World!" example for High Energy Physics analysis.  
The implementations proposed here using Apache Spark APIs are a direct "Spark translation"
of a [tutorial using ROOT DataFrame](https://root.cern.ch/doc/master/df102__NanoAODDimuonAnalysis_8py.html)

### Data
  - The original data, converted to [nanoaod format](http://cds.cern.ch/record/2752849/files/Fulltext.pdf),
    is shared in [ROOT format](https://root.cern/about/). See [Notes](#Notes) on how to access it.
  - These examples use CMS open data from 2012, made available via the CERN opendata portal:
      [DOI: 10.7483/OPENDATA.CMS.YLIC.86ZZ](http://opendata.cern.ch/record/6004)
      and [DOI: 10.7483/OPENDATA.CMS.M5AD.Y3V3)](http://opendata.cern.ch/record/6030) 
  - Data is also provided (for this work) in Apache Parquet and Apache ORC format
  - You can download the following datasets:
    - **61 million events** (2GB)
      - original files in ROOT format: root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root
      - dataset converted to **Parquet**: [Run2012BC_DoubleMuParked_Muons.parquet](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012BC_DoubleMuParked_Muons.parquet/)
      - dataset converted to **ORC**: [Run2012BC_DoubleMuParked_Muons.orc](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012BC_DoubleMuParked_Muons.orc/)
    - **6.5 billion events** (200 GB)
      - original files, in ROOT format root://eospublic.cern.ch//eos/root-eos/benchmark/CMSOpenDataDimuon
      - dataset converted to **ORC**: [CMSOpenDataDimuon_large.orc](https://sparkdltrigger.web.cern.ch/sparkdltrigger/CMSOpenDataDimuon_large.orc)
  
      
### Notebooks 
Multiple notebook solutions are provided, to illustrate different approaches with Apache Spark.  
Notes on the exeution environment:
 - The notebooks use the dataset with 61 million events (Except the SCALE test that uses 6.5 billion events)
 - Spark version: Spark 3.2.1 (except the mapInArrow example that uses 3.3.0-SNAPSHOT)
 - The Apache ORC format is used to profit from vectorized read for complex types in Spark 3.2.1
 - The machine used for testing has 4 physical CPU cores

| <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/250px-Jupyter_logo.svg.png" height="50"> Notebook                                                                                                                                                                                                     | Run Time  | Short description                                                                                                                                                                                           |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **[<img src="https://raw.githubusercontent.com/googlecolab/open_in_colab/master/images/icon128.png" height="50"> Dimuon spectrum analysis on Colab](https://colab.research.google.com/github/LucaCanali/Miscellaneous/blob/master/Spark_Physics/Dimuon_mass_spectrum/Dimuon_mass_spectrum_histogram_Spark_DataFrame_Colab_version.ipynb)** | -         | You can run this on Google's Colaboratory                                                                                                                                                                   |
| **[<img src="https://swanserver.web.cern.ch/swanserver/images/badge_swan_white_150.png" height="30"> Dimuon spectrum analysis on CERN SWAN](https://cern.ch/swanserver/cgi-bin/go/?projurl=https://raw.githubusercontent.com/LucaCanali/Miscellaneous/master/Spark_Physics/Dimuon_mass_spectrum/Dimuon_mass_spectrum_histogram_Spark_DataFrame_CERNSWAN_version.ipynb)**                                        | -         | You can run this on CERN SWAN (requires CERN SSO credentials)                                                                                                                                               |               
| [**1. DataFrame API**](Dimuon_mass_spectrum/1.Dimuon_mass_spectrum_histogram_Spark_DataFrame_ORC_vectorized.ipynb)                                                                                                                                                                                                                         | 10 sec    | The analysis is implemented using Apache Spark DataFrame API. This uses the dataset in Apache ORC format                                                                                                    |
| [**2. Spark SQL**](Dimuon_mass_spectrum/2.Dimuon_mass_spectrum_histogram_Spark_SQL_ORC_vectorized.ipynb)                                                                                                                                                                                                                                   | 10 sec    | Same as above but using Spark SQL                                                                                                                                                                           |
| [**3. DataFrame API with Parquet**](Dimuon_mass_spectrum/3.Dimuon_mass_spectrum_histogram_Spark_DataFrame_Parquet.ipynb)                                                                                                                                                                                                                   | 30 sec    | Same as 1. , but consideably slower because Apache Spark 3.2.1 does not support vectorized reads for complex types in Apache Parquet, see [SPARK-34863](https://issues.apache.org/jira/browse/SPARK-34863)  |
| [**4. Scala UDF**](Dimuon_mass_spectrum/4.Dimuon_mass_spectrum_histogram_Spark_Scala_UDF_ORC_vectorized.ipynb)                                                                                                                                                                                                                             | 10 sec    | Mixed DataFrame and Scala UDF. The dimuon invariant mass formula computation is done using a Scala UDF. Link to [Scala UDF code](Dimuon_mass_spectrum/scalaUDF/src/main/scala/ch/cern/udf/DimuonMass.scala) |
| [**5a. Pandas UDF flattened data**](Dimuon_mass_spectrum/5a.Dimuon_mass_spectrum_histogram_Spark_Pandas_flattened_data_UDF_ORC_vectorized.ipynb)                                                                                                                                                                                           | 15 sec    | Mixed DataFrame and Scala UDF. The dimuon invariant mass formula computation is done using a Python Pandas UDF                                                                                              |
| [**5b. Pandas UDF data arrays**](Dimuon_mass_spectrum/5b.Dimuon_mass_spectrum_histogram_Spark_Pandas_with_arrays_UDF_ORC_vectorized.ipynb)                                                                                                                                                                                                 | 42 sec    | Same as 5a, but the Pandas UDF uses data in arrays and lists                                                                                                                                                |
| [**6a. MapInArrow flattened data**](Dimuon_mass_spectrum/6a.Dimuon_mass_spectrum_histogram_Spark_UDF_MapInArrow_flattened_data_ORC_vectorized.ipynb)                                                                                                                                                                                  | 23 sec    | This uses mapInArrow, introduced in [SPARK-37227](https://issues.apache.org/jira/browse/SPARK-37227)                                                                                                        |
| [**6b. MapInArrow data arrays**](Dimuon_mass_spectrum/6b.Dimuon_mass_spectrum_histogram_Spark_UDF_MapInArrow_with_arrays_ORC_vectorized.ipynb)                                                                                                                                                                                        | 84 sec    | Same as 6a but the mapInArrow UDF uses data arrays                                                                                                                                                          |
| [**<span style="color:red">7. DataFrame API at scale</span>**](Dimuon_mass_spectrum/7.Dimuon_mass_spectrum_histogram_Spark_DataFrame_ORC_vectorized-Large_SCALE.ipynb)                                                                                                                                                                     | (*)33 sec | (*)This has processed 6.4 billion events, at scale on a cluster using 200 CPU cores.                                                                                                                        |

---
## 2. HEP analysis benchmark
  
This provides implementations of the High Energy Physics benchmark tasks using Apache Spark.    
It follows the [IRIS-HEP benchmark](https://github.com/iris-hep/adl-benchmarks-index) specifications
and solutions linked there.  
Solutions to the benchmark tasks are also directly inspired by the article [Evaluating Query Languages and Systems for High-Energy Physics Data](https://arxiv.org/abs/2104.12615).  
      
### Data
  - This uses CMS open data from 2012, made available via the CERN opendata portal:
    [ DOI:10.7483/OPENDATA.CMS.IYVQ.1J0W](http://opendata.cern.ch/record/6021)
  - The original data, converted to [nanoaod format](http://cds.cern.ch/record/2752849/files/Fulltext.pdf), is shared in [ROOT format](https://root.cern/about/)
  - Data is also provided in Apache Parquet and Apache ORC format
  - Datasets you can download and use for this analysis:
  - 53 million events (16 GB), original files in ROOT format: root://eospublic.cern.ch//eos/root-eos/benchmark/Run2012B_SingleMu.root
  - **53 million events** (16 GB), converted to Parquet: [Run2012BC_DoubleMuParked_Muons.parquet](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012B_SingleMu.parquet)
  - **53 million events** (16 GB), converted to ORC: [Run2012BC_DoubleMuParked_Muons.orc](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012B_SingleMu.orc)
  - **7 million events** (2 GB) ORC format [Run2012B_SingleMu_sample.orc](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012B_SingleMu_sample.orc)  
  
### Notebooks 

The notebooks use the dataset with 53 million events in Apache ORC format (to profit from vectorized read in Spark 3.2.1).

| <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/250px-Jupyter_logo.svg.png" height="50"> Notebook                                                                                                                                                                           | Short description                                                                                                                                                                                                                       |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **[<img src="https://raw.githubusercontent.com/googlecolab/open_in_colab/master/images/icon128.png" height="50"> Benchmark tasks 1 to 5 on Colab](https://colab.research.google.com/github/LucaCanali/Miscellaneous/blob/master/Spark_Physics/HEP_benchmark/ADL_HEP_Query_Benchmark_Q1_Q5_Colab_Version.ipynb)** | You can run this on Google's Colaboratory                                                                                                                                                                                               |
| **[<img src="https://swanserver.web.cern.ch/swanserver/images/badge_swan_white_150.png" height="30"> Benchmark tasks 1 to 5 on CERN SWAN](https://cern.ch/swanserver/cgi-bin/go/?projurl=https://raw.githubusercontent.com/LucaCanali/Miscellaneous/master/Spark_Physics/HEP_benchmark/ADL_HEP_Query_Benchmark_Q1_Q5_CERNSWAN_Version.ipynb)**         | You can run this on CERN SWAN (requires CERN SSO credentials)  |                     
| [**Benchmark tasks 1 to 5**](HEP_benchmark/ADL_HEP_Query_Benchmark_Q1_Q5.ipynb)                                                                                                                                                                                                                                  | The analysis is implemented using Apache Spark DataFrame API. Uses the dataset in Apache ORC format                                                                                                                                     |
| [**Benchmark task 6**](HEP_benchmark/ADL_HEP_Query_Benchmark_Q6.ipynb)                                                                                                                                                                                                                                           | Three different solution are provided. This is the hardest task to implement in Spark. The proposed solutions use also Scala UDFs: link to [the Scala UDF code](HEP_benchmark/scalaUDF/src/main/scala/ch/cern/udf/HEPBenchmarkQ6.scala) |
| [**Benchmark task 7**](HEP_benchmark/ADL_HEP_Query_Benchmark_Q7.ipynb)                                                                                                                                                                                                                                           | Two different solutions provided, one using the explode function, the oder with Spark's higher order functions for array processing                                                                                                     |
| [**Benchmark task 8**](HEP_benchmark/ADL_HEP_Query_Benchmark_Q8.ipynb)                                                                                                                                                                                                                                           | This combines Spark DataFarme API for filtering and Scala UDFs for processing. Link to [the Scala UDF code](HEP_benchmark/scalaUDF/src/main/scala/ch/cern/udf/HEPBenchmarkQ8.scala)                                                     |

---
## 3. LHCb outreach-style analysis
This notebook is an example of how to use Spark to perform a simple analysis using high energy physics data from a LHC experiment.
**Credits:**
* The original text of this notebook, including all exercises, analysis, explanations and data have been developed by the 
LHCb collaboration and are authored and shared by the LHCb collaboration in their opendata and outreach efforts. See links:
    * https://github.com/lhcb/opendata-project/blob/master/LHCb_Open_Data_Project.ipynb
    * "Undergraduate Laboratory Experiment: Measuring Matter Antimatter Asymmetries at the Large Hadron Collide" https://cds.cern.ch/record/1994172?ln=en
    * http://www.hep.manchester.ac.uk/u/parkes/LHCbAntimatterProjectWeb/LHCb_Matter_Antimatter_Asymmetries/Homepage.html
  
### Data
  - The notebook presented here uses datasets in Apache Parquet format:
    - (1.2 GB) download from: [LHCb_opendata_notebook_data](https://sparkdltrigger.web.cern.ch/sparkdltrigger/LHCb_opendata) 
- The original work uses LHCb opendata made available via the CERN opendata portal:
  [PhaseSpaceSimulation.root](http://opendata.cern.ch/eos/opendata/lhcb/AntimatterMatters2017/data/PhaseSpaceSimulation.root),
  [B2HHH_MagnetDown.root](http://opendata.cern.ch/eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root)
  [B2HHH_MagnetUp.root](http://opendata.cern.ch/eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetUp.root)
  
### Notebooks
   - **[<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/250px-Jupyter_logo.svg.png" height="50">LHCb opendata analysis notebook](LHCb_opendata/LHCb_OpenData_Spark.ipynb)**
   - **[<img src="https://raw.githubusercontent.com/googlecolab/open_in_colab/master/images/icon128.png" height="50">Run LHCb opendata analysis notebook on Colab](https://colab.research.google.com/github/LucaCanali/Miscellaneous/blob/master/Spark_Physics/LHCb_opendata/LHCb_OpenData_Spark.ipynb)**
   - **[<img src="https://swanserver.web.cern.ch/swanserver/images/badge_swan_white_150.png" height="30"> Run LHCb opendata analysis notebook in CERN SWAN (requires CERN SSO credentials](https://cern.ch/swanserver/cgi-bin/go/?projurl=https://raw.githubusercontent.com/LucaCanali/Miscellaneous/master/Spark_Physics/LHCb_opendata/LHCb_OpenData_Spark_CERNSWAN_Version.ipynb)**
---


## Notes on reading and converting data stored in ROOT format
  - If you need to convert data in ROOT format to Apache Parquet or ORC:
     - You can use Spark and the Laurelin library, as detailed in [this note on converting from ROOT format](Spark_Root_data_preparation.md)
     - You can use Python toolkits, notably uproot and awkward arrays, as [in this example of using uproot] 
  - If you need to access data shared via the XRootD protocol, as it is the 
  case when reading from URLs like `root://eospublic.cern.ch/..`
    - You can use Apache Spark with the [Hadoop-XRootD connector](https://github.com/cerndb/hadoop-xrootd)
    - You can use the toolset from [XRootD project](https://xrootd.slac.stanford.edu/)
      - CLI example: `xrdcp root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root .`

## Physics
A few links with additional details on the terms and formulas used:  
  - https://github.com/iris-hep/adl-benchmarks-index/blob/master/reference.md
  - http://edu.itp.phys.ethz.ch/hs10/ppp1/2010_11_02.pdf
  - https://en.wikipedia.org/wiki/Invariant_mass
    
