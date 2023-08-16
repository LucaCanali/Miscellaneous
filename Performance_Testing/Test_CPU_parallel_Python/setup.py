#!/usr/bin/env python

from setuptools import setup, find_packages

description = "test-CPU-parallel is a basic CPU workload generator."

long_description = """
test_CPU_parallel.py - A basic CPU workload generator.  
Luca.Canali@cern.ch - April 2023  

Use test_CPU_parallel to generate CPU-intensive load on a system, running multiple threads in parallel.  
The tool runs a CPU-burning loop concurrently on the system, with configurable parallelism.  
The tool outputs a measurement of the CPU-burning loop execution time as a function of load.  

### How to use test_CPU_parallel.py from the command line
```
Example:
# Install with pip or clone from GitHub
pip install test-CPU-parallel

# run one-off data collection with 2 concurrent workers
test_CPU_parallel.py --num_workers 2 

# Measure job runtime over a ramp of concurrent workers from 1 to 8, and output the results to a CSV file
test_CPU_parallel.py --num_workers 8 --full --output myout.csv 

Parameters:

--full - Full mode will test all the values of num_workers from 1 to the value 
         set with --num_workers, use this to collect speedup test measurements and create plots, default = False
--output - Optional output file, applies only to the full mode, default = None
--num_workers - Number of parallel threads running concurrently, default = 2
--num_job_execution_loops - number of times the execution loop is run on each worker, default = 3
--worker_inner_loop_size - internal weight of the inner execution loop, default = 100000000
```

### How to use test_CPU_parallel programmatically

You have the ability to employ the test_CPU_parallel function within your Python scripts, including its integration 
into Continuous Integration (CI) tests. This proves advantageous for tasks like quantifying system performance and 
assessing how well the CPU adapts to varying workloads. This becomes especially handy when you're comparing test runs
conducted on different occasions or on distinct computer setups.  
In your code, the process of executing the test and obtaining results is as follows:
```
pip install test-CPU-parallel
from test_CPU_parallel import test_CPU_parallel

# See also the configuration options in the help
test = test_CPU_parallel()

# Run a test
test.test_one_load()

# Run a full run
test.test_full()
```


"""

setup(name='Test_CPU_parallel',
    version='1.0.4',
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Luca Canali',
    author_email='luca.canali@cern.ch',
    url='https://github.com/LucaCanali/Miscellaneous/tree/master/Performance_Testing/Test_CPU_parallel_Python',
    license='Apache License, Version 2.0',
    include_package_data=True,
    packages=find_packages(),
    scripts=['test_CPU_parallel/test_CPU_parallel.py'],
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=[],
    classifiers=[
    'Programming Language :: Python :: 3',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: Apache Software License',
    'Intended Audience :: Developers',
    'Development Status :: 4 - Beta',
    ]
    )
