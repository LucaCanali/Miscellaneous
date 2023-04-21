# Oracle testing using SLOB
SLOB a tool that runs on top of Oracle databases for load testing and specifically stresses Physical and Logical IO.  
In the configuration used for these tests we only stressed Logical IO, that is accessing blocks from the Oracle buffer cache (memory).  
The tool creates test tables on the database and performs block IO reading from the test tables with a tunable number of concurrent workers.  

## SLOB installation and configuration
- Create a test database with a buffer cache large enough to cache the SLOB test tables 
- Download SLOB and documentation, see https://kevinclosson.net/slob/
- Create a SLOB tablespace and install the test users `./setup.sh SLOB 16`
    - note key config in the slob.conf file used for the tests reported here 
  ```
  UPDATE_PCT=0
  SCAN_PCT=0
  RUN_TIME=300
  WORK_LOOP=0
  SCALE=16G
  SCAN_TABLE_SZ=1M
  WORK_UNIT=256
  REDO_STRESS=LITE
  LOAD_PARALLEL_DEGREE=2  
  ```

## SLOB usage
- Run the test with a given number of concurrent workers, for example 2: `./runit.sh 2`
- Collect the results from the metrics in the AWR report
  - check that the workload was cached-reads only when testing for Logical I/O
  - the number of Logical IOs per second is the key metric to look at

## Results
- Example metrics are in [Data](Data)
- Example Notebooks with metrics analysis are in [Notebooks](Notebooks)
