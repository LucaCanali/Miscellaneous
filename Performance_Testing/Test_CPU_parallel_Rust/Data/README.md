# Data - Tests Results

## test_CPU_parallel_Rust  
Results of CPU load testing using test_cpu_parallel version 1.1.0

How to run the tests:
```
./test_cpu_parallel -w 40 --full --output_file test_cpu_parallel_rust_RAC55.csv
./test_cpu_parallel -w 70 --full --output_file test_cpu_parallel_rust_HDP6.csv
./test_cpu_parallel -w 24 --full --output_file test_cpu_parallel_rust_RAC52.csv
./test_cpu_parallel -w 48 --full --output_file test_cpu_parallel_rust_RAC54.csv
```

Results:  
- Note these were gathered with test_cpu_parallel version 1.0.1 (compiled with Cargo 1.68.2)
- [test_cpu_parallel_rust_HDP6.csv](test_cpu_parallel_rust_HDP6.csv)
- [test_cpu_parallel_rust_RAC55.csv](test_cpu_parallel_rust_RAC55.csv)
- [test_cpu_parallel_rust_RAC52.csv](test_cpu_parallel_rust_RAC52.csv)
- [test_cpu_parallel_rust_RAC54.csv](test_cpu_parallel_rust_RAC54.csv)

See also [Notebooks](../Notebooks) for analysis of the data.

