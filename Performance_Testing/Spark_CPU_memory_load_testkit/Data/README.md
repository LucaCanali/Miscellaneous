# Data - Tests Results

## Spark CPU and memory load testing kit 
Results of testing the CPU and memory load testing kit using the `test_Spark_CPU_memory_sparkmeasure.py` script.
Note the tests were run on relatively large nodes with 512GB of RAM and 64 cores.

How the tests were run:    
```
./test_Spark_CPU_memory.py -w 70 --full --output ttest_Spark_CPU_memory_sparkmeasure_HDP6_1_70.csv   
./test_Spark_CPU_memory.py -w 40 --full --output test_Spark_CPU_memory_sparkmeasure_RAC55_1_40.csv
```  

Results:  
- [test_Spark_CPU_memory_sparkmeasure_HDP6_1_70.csv](test_Spark_CPU_memory_sparkmeasure_HDP6_1_70.csv)  
- [test_Spark_CPU_memory_sparkmeasure_RAC55_1_40.csv](test_Spark_CPU_memory_sparkmeasure_RAC55_1_40.csv)  

See also [Notebooks](../Notebooks) for data analysis.

## Memory throughput measure with OS tools
Measurements of memory throughput taken while running a memory-intensive workload with `test_Spark_CPU_memory_sparkmeasure.py`   
[memory_throughput_HDP6.csv](memory_throughput_HDP6.csv)  
[memory_throughput_RAC55.csv](memory_throughput_RAC55.csv)  

Measurements were taken on AMD systems using AMD uProf (“MICRO-prof”) tool:   
`/opt/AMDuProf_4.0-341/bin/AMDuProfPcm -m memory -a -d 20 -C -A system`  

Note for Intel CPUs the equivalent tool would be pcm-memory, see also
[Tools_Linux_Memory_Perf_Measure.md](../../../Spark_Notes/Tools_Linux_Memory_Perf_Measure.md)
