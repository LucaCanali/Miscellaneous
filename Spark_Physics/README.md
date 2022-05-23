# Apache Spark for High Energy Physics
  
This collects a few simple examples of how Apache Spark can be used in the domain of High Energy Physics data analysis.  
Most of the examples are just for education purposes, use a small subset of data and can be run on laptop-sized computing resources.  
See also the blog post [Can High Energy Physics Analysis Profit from Apache Spark APIs?](https://db-blog.web.cern.ch/node/186)  

### Contents:
 1. **[Dimuon mass spectrum analysis](#1-dimuon-mass-spectrum-analysis)**
 2. **[HEP analysis benchmark](#2-hep-analysis-benchmark)**
 3. **[ATLAS Higgs analysis](#3-atlas-higgs-boson-analysis---outreach-style)**
 4. **[CMS Higgs analysis](#4-cms-higgs-boson-analysis---outreach-style)**
 5. **[LHCb matter antimatter analysis](#5-lhcb-matter-antimatter-asymmetries-analysis---outreach-style)**
 - **[How to convert from ROOT format to Apache Parquet and ORC](#notes-on-reading-and-converting-from-root-format-to-parquet-and-orc)**
 - **[Physics references](#physics-references)**
---
## 1. Dimuon mass spectrum analysis
  
This is a sort of "Hello World!" example for High Energy Physics analysis.  
The implementations proposed here using Apache Spark APIs are a direct "Spark translation"
of a [tutorial using ROOT DataFrame](https://root.cern.ch/doc/master/df102__NanoAODDimuonAnalysis_8py.html)

### Data
  - These examples use CMS open data from 2012, made available via the CERN opendata portal:
      [DOI: 10.7483/OPENDATA.CMS.YLIC.86ZZ](http://opendata.cern.ch/record/6004)
      and [DOI: 10.7483/OPENDATA.CMS.M5AD.Y3V3)](http://opendata.cern.ch/record/6030) 
    - The original data, converted to [nanoaod format](http://cds.cern.ch/record/2752849/files/Fulltext.pdf),
      is shared in [ROOT format](https://root.cern/about/). 
  - Data has been converted and made available for this work in snappy-compressed Apache Parquet and Apache ORC formats
  - You can download the following datasets:
    - **61 million events** (2 GB)
      - original files in ROOT format: root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root
        - see [notes](#notes-on-reading-and-converting-data-from-root-format) on how to access data using the XRootD protocol (`root://`) and how to read it.
      - dataset converted to **Parquet**: [Run2012BC_DoubleMuParked_Muons.parquet](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012BC_DoubleMuParked_Muons.parquet)
      - dataset converted to **ORC**: [Run2012BC_DoubleMuParked_Muons.orc](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012BC_DoubleMuParked_Muons.orc)
    - **6.5 billion events** (200 GB, this is the 2GB dataset repeated 105 times)
      - original files, in ROOT format root://eospublic.cern.ch//eos/root-eos/benchmark/CMSOpenDataDimuon
      - dataset converted to **Parquet**: [CMSOpenDataDimuon_large.parquet](https://sparkdltrigger.web.cern.ch/sparkdltrigger/CMSOpenDataDimuon_large.parquet)
          - download using `wget -r -np -R "index.html*" -e robots=off https://sparkdltrigger.web.cern.ch/sparkdltrigger/CMSOpenDataDimuon_large.parquet/`
      - dataset converted to **ORC**: [CMSOpenDataDimuon_large.orc](https://sparkdltrigger.web.cern.ch/sparkdltrigger/CMSOpenDataDimuon_large.orc)
        - download using `wget -r -np -R "index.html*" -e robots=off https://sparkdltrigger.web.cern.ch/sparkdltrigger/CMSOpenDataDimuon_large.orc/`

      
### Notebooks 
Multiple notebook solutions are provided, to illustrate different approaches with Apache Spark.  
Notes on the execution environment:
 - The notebooks use the dataset with 61 million events (Except the SCALE test that uses 6.5 billion events)
 - Spark version: These notebooks have been tested with Spark 3.2.1 and Spark 3.3.0
 - Notable features in Spark 3.3.0 used: Apache Spark vectorized reader for complex types in Parquet, mapInArrow UDF.
 - The server/VM used as Spark driver for testing and measuring the execution time has 4 physical CPU cores, an SSD disk, and 32 GB of RAM (which is more than the minimum requirements for running this workload)

| <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/250px-Jupyter_logo.svg.png" height="50"> Notebook                                                                                                                                                                                                                                 | Run Time  | Short description                                                                                                                                                                                                                                     |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [**1a. DataFrame API**](Dimuon_mass_spectrum/1a.Dimuon_mass_spectrum_histogram_Spark_DataFrame_Parquet.ipynb)                                                                                                                                                                                                                                                          | 11 sec    | The analysis is implemented using Apache Spark DataFrame API. This uses the dataset in Apache Parquet format                                                                                                                                          |
| [**1b. DataFrame API**](Dimuon_mass_spectrum/1b.Dimuon_mass_spectrum_histogram_Spark_DataFrame_ORC.ipynb)                                                                                                                                                                                                                                                              | 11 sec    | Same as 1a., with the exception that this uses the dataset in Apache ORC format                                                                                                                                                                       |
| [**2. Spark SQL**](Dimuon_mass_spectrum/2.Dimuon_mass_spectrum_histogram_Spark_SQL.ipynb)                                                                                                                                                                                                                                                                              | 11 sec    | The analysis is implemented using Spark SQL                                                                                                                                                                                                           |
| [**3. DataFrame API with Parquet non vectorized**](Dimuon_mass_spectrum/3.Dimuon_mass_spectrum_histogram_Spark_DataFrame_Parquet_NonVectorized.ipynb)                                                                                                                                                                                                                 | 28 sec    | Same as (1a.) but considerably slower by disabling the option for vectorized reads for complex types in Apache Parquet                                                                                                                                |
| [**4. Scala UDF**](Dimuon_mass_spectrum/4.Dimuon_mass_spectrum_histogram_Spark_Scala_UDF.ipynb)                                                                                                                                                                                                                                                                        | 12 sec    | Implementation that mixes DataFrame API and Scala UDF. The dimuon invariant mass formula computation is implemented using a UDF written in Scala. Link to [Scala UDF code](Dimuon_mass_spectrum/scalaUDF/src/main/scala/ch/cern/udf/DimuonMass.scala) |
| [**5a. Pandas UDF flattened data**](Dimuon_mass_spectrum/5a.Dimuon_mass_spectrum_histogram_Spark_Pandas_flattened_data_UDF.ipynb)                                                                                                                                                                                                                                      | 19 sec    | Implementation that mixes DataFrame API and Python Pandas UDF. The dimuon invariant mass formula computation is implemented using a  Pandas UDF                                                                                                       |
| [**5b. Pandas UDF data arrays**](Dimuon_mass_spectrum/5b.Dimuon_mass_spectrum_histogram_Spark_Pandas_full_formula_with_arrays_UDF.ipynb)                                                                                                                                                                                                                               | 82 sec    | Same as 5a, but the Pandas UDF in this case uses data in arrays and lists                                                                                                                                                                             |
| [**5c. Pandas UDF data arrays optimized**](Dimuon_mass_spectrum/5c.Dimuon_mass_spectrum_histogram_Spark_Pandas_optimized_formula_with_arrays_UDF.ipynb)                                                                                                                                                                                                                | 64 sec    | Same as 5b, but using an approximated formula for mass calculation that substantially reduces the amount of calculations performed                                                                                                                    |
| [**6a. MapInArrow flattened data**](Dimuon_mass_spectrum/6a.Dimuon_mass_spectrum_histogram_Spark_UDF_MapInArrow_flattened_data.ipynb)                                                                                                                                                                                                                                  | 22 sec    | This uses mapInArrow, introduced in [SPARK-37227](https://issues.apache.org/jira/browse/SPARK-37227)                                                                                                                                                  |
| [**6b. MapInArrow data arrays**](Dimuon_mass_spectrum/6b.Dimuon_mass_spectrum_histogram_Spark_UDF_MapInArrow_with_arrays.ipynb)                                                                                                                                                                                                                                        | 83 sec    | Same as 6a but the mapInArrow UDF uses data arrays                                                                                                                                                                                                    |
| [**7. RumbleDB on Spark**](Dimuon_mass_spectrum/7.Dimuon_mass_spectrum_histogram_RumbleDB_on_Spark.ipynb)                                                                                                                                                                                                                                                              | 166 sec   | This implementation runs with RumbleDB query engine on top of Apache Spark. RumbleDB implements the JSONiq language.                                                                                                                                  |
| [**<span style="color:red">8. DataFrame API at scale</span>**](Dimuon_mass_spectrum/8.Dimuon_mass_spectrum_histogram_Spark_DataFrame_ORC_vectorized-Large_SCALE.ipynb)                                                                                                                                                                                                 | (*)33 sec | (*)This has processed 6.5 billion events, at scale on a cluster using 200 CPU cores.                                                                                                                                                                  |
| **[<img src="https://raw.githubusercontent.com/googlecolab/open_in_colab/master/images/icon128.png" height="50"> Dimuon spectrum analysis on Colab](https://colab.research.google.com/github/LucaCanali/Miscellaneous/blob/master/Spark_Physics/Dimuon_mass_spectrum/Dimuon_mass_spectrum_histogram_Spark_DataFrame_Colab_version.ipynb)**                             | -         | You can run this on Google's Colaboratory                                                                                                                                                                                                             |
| **[<img src="https://swanserver.web.cern.ch/swanserver/images/badge_swan_white_150.png" height="30"> Dimuon spectrum analysis on CERN SWAN](https://cern.ch/swanserver/cgi-bin/go/?projurl=https://raw.githubusercontent.com/LucaCanali/Miscellaneous/master/Spark_Physics/Dimuon_mass_spectrum/Dimuon_mass_spectrum_histogram_Spark_DataFrame_CERNSWAN_version.ipynb)** | -         | You can run this on CERN SWAN (requires CERN SSO credentials)                                                                                                                                                                                         |               

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
  - Data has been converted and made available for this work in snappy-compressed Apache Parquet and Apache ORC formats
  - Datasets you can download and use for this analysis:
  - 53 million events (16 GB), original files in ROOT format: root://eospublic.cern.ch//eos/root-eos/benchmark/Run2012B_SingleMu.root
    - see [notes](#notes-on-reading-and-converting-data-from-root-format) on how to access data using the XRootD protocol (`root://`) and how to read it.
  - **53 million events** (16 GB), converted to Parquet: [Run2012BC_DoubleMuParked_Muons.parquet](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012B_SingleMu.parquet)
    - download using `wget -r -np -R "index.html*" -e robots=off https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012B_SingleMu.parquet/` 
  - **53 million events** (16 GB), converted to ORC: [Run2012BC_DoubleMuParked_Muons.orc](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012B_SingleMu.orc)
    - download using `wget -r -np -R "index.html*" -e robots=off https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012B_SingleMu.orc/` 
  - **7 million events** (2 GB) ORC format [Run2012B_SingleMu_sample.orc](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012B_SingleMu_sample.orc)  
  - **7 million events** (2 GB) Parquet format [Run2012B_SingleMu_sample.parquet](https://sparkdltrigger.web.cern.ch/sparkdltrigger/Run2012B_SingleMu_sample.parquet)
  
### Notebooks 

Notes on the execution environment:
- The notebooks can be run using the datasets with 53 million events for more accuracy or with the reduced dataset with 7 million events for faster execution
- Spark version: These notebooks have been tested with Spark 3.2.1 and Spark 3.3.0
- Notable features in Spark 3.3.0 used: Apache Spark vectorized reader for complex types in Parquet
- The server/VM used as Spark driver for testing and measuring the execution time has 4 physical CPU cores, an SSD disk, and 32 GB of RAM (which is more than the minimum requirements for running this workload)

| <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/250px-Jupyter_logo.svg.png" height="50"> Notebook                                                                                                                                                                                                         | Short description                                                                                                                                                                                                                        |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [**Benchmark tasks 1 to 5**](HEP_benchmark/ADL_HEP_Query_Benchmark_Q1_Q5.ipynb)                                                                                                                                                                                                                                                                | The analysis is implemented using Apache Spark DataFrame API and uses the dataset in Apache ORC format.                                                                                                                                  |
| [**Benchmark tasks 1 to 5, using Parquet and SparkHistogram**](HEP_benchmark/ADL_HEP_Query_Benchmark_Q1_Q5_Parquet_sparkhistogram.ipynb)                                                                                                                                                                                                       | The analysis using Apache Spark DataFrame API, same as above. MOdifications: it uses the dataset in Apache Parquet format and histogram generation with the sparkhistogram pacakge.                                                      |
| [**Benchmark task 6**](HEP_benchmark/ADL_HEP_Query_Benchmark_Q6.ipynb)                                                                                                                                                                                                                                                                         | Three different solution are provided. This is the hardest task to implement in Spark. The proposed solutions use also Scala UDFs: link to [the Scala UDF code.](HEP_benchmark/scalaUDF/src/main/scala/ch/cern/udf/HEPBenchmarkQ6.scala) |
| [**Benchmark task 7**](HEP_benchmark/ADL_HEP_Query_Benchmark_Q7.ipynb)                                                                                                                                                                                                                                                                         | Two different solutions provided, one using the explode function, the other with Spark's higher order functions for array processing.                                                                                                    |
| [**Benchmark task 8**](HEP_benchmark/ADL_HEP_Query_Benchmark_Q8.ipynb)                                                                                                                                                                                                                                                                         | This combines Spark DataFrame API for filtering and Scala UDFs for processing. Link to [the Scala UDF code.](HEP_benchmark/scalaUDF/src/main/scala/ch/cern/udf/HEPBenchmarkQ8.scala)                                                     |
| **[<img src="https://raw.githubusercontent.com/googlecolab/open_in_colab/master/images/icon128.png" height="50"> Benchmark tasks 1 to 5 on Colab](https://colab.research.google.com/github/LucaCanali/Miscellaneous/blob/master/Spark_Physics/HEP_benchmark/ADL_HEP_Query_Benchmark_Q1_Q5_Colab_Version.ipynb)**                               | You can run this on Google's Colaboratory.                                                                                                                                                                                               |
| **[<img src="https://swanserver.web.cern.ch/swanserver/images/badge_swan_white_150.png" height="30"> Benchmark tasks 1 to 5 on CERN SWAN](https://cern.ch/swanserver/cgi-bin/go/?projurl=https://raw.githubusercontent.com/LucaCanali/Miscellaneous/master/Spark_Physics/HEP_benchmark/ADL_HEP_Query_Benchmark_Q1_Q5_CERNSWAN_Version.ipynb)** | You can run this on CERN SWAN (requires CERN SSO credentials).                                                                                                                                                                           |                     

---
## 3. ATLAS Higgs boson analysis - outreach-style
This is an example analysis of the Higgs boson detection via the decay channel H &rarr; ZZ* &rarr; 4l
From the decay products measured at the ATLAS experiment and provided as open data, you will be able to produce a few histograms,
comparing experimental data and Monte Carlo (simulation) data. From there you can infer the invariant mass of the Higgs boson.  
Disclaimer: this is for educational purposes only, it is not the code nor the data of the official Higgs boson discovery paper.  
It is based on the original work on [ATLAS outreach notebooks](https://github.com/atlas-outreach-data-tools/notebooks-collection-opendata/tree/master/13-TeV-examples/uproot_python)
and derived [work at this repo](https://github.com/gordonwatts/pyhep-2021-SX-OpenDataDemo) and [this work](https://root.cern/doc/master/df106__HiggsToFourLeptons_8py.html) 
Reference: ATLAS paper on the [discovery of the Higgs boson](https://www.sciencedirect.com/science/article/pii/S037026931200857X) (mostly Section 4 and 4.1)   

### Data
  - The original data in ROOT format is from the [ATLAS Open Datasets](http://opendata.atlas.cern/release/2020/documentation/)
    - direct link: [ATLAS open data events selected with at least four leptons (electron or muon)](https://atlas-opendata.web.cern.ch/atlas-opendata/samples/2020/4lep.zip)
  - The notebooks presented here use datasets from the original open data events converted to snappy-compressed Apache Parquet format. 
    - Download from: [ATLAS Higgs notebook opendata in Parquet format](https://sparkdltrigger.web.cern.ch/sparkdltrigger/ATLAS_Higgs_opendata)
      - download all files (200 MB) using `wget -r -np -R "index.html*" -e robots=off https://sparkdltrigger.web.cern.ch/sparkdltrigger/ATLAS_Higgs_opendata/`

### Notebooks

  - Tested with Spark 3.2.1 and 3.3.0
  - These analyses use a very small dataset and are mostly intended to show how the Spark API can be applied in this context,
    rather than its performance and scalability.

| <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/250px-Jupyter_logo.svg.png" height="50"> Notebook                                                                                                                                                                                                                  | Short description                                                                                                                                                                                       |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **[1. ATLAS opendata Higgs H-ZZ*-4l basic analysis](ATLAS_Higgs_opendata/H_ZZ_4l_analysis_basic_experiment_data.ipynb)**                                                                                                                                                                                                                                | Basic analysis with experiment (detector) data.                                                                                                                                                         |
| **[2. H-ZZ*-4l basic analysis with additional filters and cuts](ATLAS_Higgs_opendata/H_ZZ_4l_analysis_extra_cuts_montecarlo_data.ipynb)**                                                                                                                                                                                                               | Analysis with extra cuts and data operations, this uses Monte Carlo (simulation) data.                                                                                                                  |
| **[3. H-ZZ*-4l reproduce Fig 2 of the paper - with experiment data and monte carlo](ATLAS_Higgs_opendata/H_ZZ_4l_analysis_data_and_monte_carlo_Fig2_Higgs_paper.ipynb)**                                                                                                                                                                                | Analysis with extra cuts and data operations, this uses experiment (detector) data and Monte Carlo (simulation) data for signal and backgroud. It roughly reproduces Figure 2 of the ATLAS Higgs paper. |
| **[<img src="https://raw.githubusercontent.com/googlecolab/open_in_colab/master/images/icon128.png" height="50">Run ATLAS opendata Higgs H-ZZ*-4l basic analysis on Colab](https://colab.research.google.com/github/LucaCanali/Miscellaneous/blob/master/Spark_Physics/ATLAS_Higgs_opendata/H_ZZ_4l_analysis_basic_experiment_data.ipynb)**             | Basic analysis with experiment (detector) data. This notebook opens on Google's Colab.                                                                                                                  |
| **[<img src="https://swanserver.web.cern.ch/swanserver/images/badge_swan_white_150.png" height="30"> Run ATLAS opendata Higgs H-ZZ*-4l basic analysis on CERN SWAN](https://cern.ch/swanserver/cgi-bin/go/?projurl=https://raw.githubusercontent.com/LucaCanali/Miscellaneous/master/Spark_Physics/ATLAS_Higgs_opendata/H_ZZ_4l_analysis_basic.ipynb)** | Basic analysis with experiment (detector) data. This notebook opens on CERN's SWAN notebook service (requires CERN SSO credentials)                                                                     |

---
## 4. CMS Higgs boson analysis - outreach-style
This is an example analysis of the Higgs boson detection via the decay channel H &rarr; ZZ* &rarr; 4l
Disclaimer: this is for educational purposes only, it is not the code nor the data of the official Higgs boson discovery paper.  
It is based on the original work on [cms opendata notebooks](https://github.com/cms-opendata-analyses/HiggsExample20112012) and this [derived work](https://root.cern/doc/master/df103__NanoAODHiggsAnalysis_8py.html)  
Reference: link to the [original article with CMS Higgs boson discovery](https://inspirehep.net/record/1124338)

### Data
- The original data in ROOT format is from the CMS open data
   - download from [this folder](root://eospublic.cern.ch//eos/root-eos/cms_opendata_2012_nanoaod)
   - see [notes](#notes-on-reading-and-converting-data-from-root-format) on how to access data using the XRootD protocol (`root://`) and how to read it.
  - The notebooks presented here use datasets from the original open data events converted to snappy-compressed Apache Parquet format.
    - Download from: [CMS Higgs notebook opendata in Parquet format](https://sparkdltrigger.web.cern.ch/sparkdltrigger/CMS_Higgs_opendata)
      - download all files (12 GB) using `wget -r -np -R "index.html*" -e robots=off https://sparkdltrigger.web.cern.ch/sparkdltrigger/CMS_Higgs_opendata/`

### Notebooks
| <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/250px-Jupyter_logo.svg.png" height="50"> Notebook | Short description                                                    |
|----------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| **[CMS opendata Higgs H-ZZ*-4l, basic with monte carlo signal](CMS_Higgs_opendata/H_ZZ_4l_analysis_basic_monte_carlo_signal.ipynb)**   | Basic analysis and visualization with Monte Carlo (simulation) data. |
| TBC                                                                                                                                    |                                                                      |

---
## 5. LHCb matter antimatter asymmetries analysis - outreach-style
This notebook provides an example of how to use Spark to perform a simple analysis using high energy physics data from a LHC experiment.
**Credits:**
* The original text of this notebook, including all exercises, analysis, explanations and data have been developed by the 
LHCb collaboration and are authored and shared by the LHCb collaboration in their open data and outreach efforts. See links:
    * https://github.com/lhcb/opendata-project/blob/master/LHCb_Open_Data_Project.ipynb
    * "Undergraduate Laboratory Experiment: Measuring Matter Antimatter Asymmetries at the Large Hadron Collide" https://cds.cern.ch/record/1994172?ln=en
    * http://www.hep.manchester.ac.uk/u/parkes/LHCbAntimatterProjectWeb/LHCb_Matter_Antimatter_Asymmetries/Homepage.html
  
### Data
  - The notebook presented here uses datasets in Apache Parquet format:
    - (1.2 GB) download from: [LHCb_opendata_notebook_data](https://sparkdltrigger.web.cern.ch/sparkdltrigger/LHCb_opendata) 
    - download all files using `wget -r -np -R "index.html*" -e robots=off https://sparkdltrigger.web.cern.ch/sparkdltrigger/LHCb_opendata/`
  - The original work uses LHCb open data made available via the CERN opendata portal:
  [PhaseSpaceSimulation.root](http://opendata.cern.ch/eos/opendata/lhcb/AntimatterMatters2017/data/PhaseSpaceSimulation.root),
  [B2HHH_MagnetDown.root](http://opendata.cern.ch/eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root)
  [B2HHH_MagnetUp.root](http://opendata.cern.ch/eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetUp.root)
  
### Notebooks
| <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jupyter_logo.svg/250px-Jupyter_logo.svg.png" height="50"> Notebook                                                                                                                                                                                                            | Short description                                                                 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **[LHCb outreach analysis](LHCb_opendata/LHCb_OpenData_Spark.ipynb)**                                                                                                                                                                                                                                                                             | LHCb analysis notebook using open data                                            |
 | **[<img src="https://raw.githubusercontent.com/googlecolab/open_in_colab/master/images/icon128.png" height="50">Run LHCb opendata analysis notebook on Colab](https://colab.research.google.com/github/LucaCanali/Miscellaneous/blob/master/Spark_Physics/LHCb_opendata/LHCb_OpenData_Spark.ipynb)**                                              | This notebook opens on Google's Colab                                |
| **[<img src="https://swanserver.web.cern.ch/swanserver/images/badge_swan_white_150.png" height="30"> Run LHCb opendata analysis notebook on CERN SWAN](https://cern.ch/swanserver/cgi-bin/go/?projurl=https://raw.githubusercontent.com/LucaCanali/Miscellaneous/master/Spark_Physics/LHCb_opendata/LHCb_OpenData_Spark_CERNSWAN_Version.ipynb)** | This notebook opens on CERN SWAN notebook service (requires CERN SSO credentials) |

---

## Notes on reading and converting data from ROOT format
  - **How to convert from ROOT format to Apache Parquet or ORC:**
     - You can use Spark and the Laurelin library, as detailed in [this note on converting from ROOT format](Spark_Root_data_preparation.md)
     - You can use Python toolkits, notably uproot and awkward arrays, as in this [example of how to use uproot](Uproot_example.md)
  - **How to read files via the XRootD protocol**
    - This is relevant for CERN opendata, typically shared at URLs like `root://eospublic.cern.ch/..`
    - You can use Apache Spark with the [Hadoop-XRootD connector](https://github.com/cerndb/hadoop-xrootd)
    - You can use the toolset from [XRootD project](https://xrootd.slac.stanford.edu/)
      - CLI example: `xrdcp root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root .`

## Physics references
A few links with additional details on the terms and formulas used:  
  - https://github.com/iris-hep/adl-benchmarks-index/blob/master/reference.md
  - http://edu.itp.phys.ethz.ch/hs10/ppp1/2010_11_02.pdf
  - https://en.wikipedia.org/wiki/Invariant_mass
  - "Facts And Mysteries In Elementary Particle Physics", by Martinus Veltman, WSPC, 2018.
