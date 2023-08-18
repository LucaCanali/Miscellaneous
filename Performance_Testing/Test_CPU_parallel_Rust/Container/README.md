# How to create and use a docker image for running test_cpu_parallel

This creates a docker image for test_cpu_parallel, a CPU load testing tool written in Rust.  

- Copy the test_cpu_parallel binary executable for Linux to this directory
  - Option 1, build from source and copy the executable in this directory
    - See details of how to build in the [Code_test_CPU_Rust](../Code_test_CPU_Rust) folder
  - Option 2, download the binary executable from this link:
    ```
    wget https://canali.web.cern.ch/res/test_cpu_parallel.gz
    gunzip test_cpu_parallel.gz
    chmod +x test_cpu_parallel
    ```
- Build the docker image with:
```
docker build -t lucacanali/test_cpu_parallel:v1.0 .
docker push lucacanali/test_cpu_parallel:v1.0

docker tag lucacanali/test_cpu_parallel:v1.0 lucacanali/test_cpu_parallel:latest
docker push lucacanali/test_cpu_parallel:latest
```

You can use the image to run test_cpu_parallel in a container as in:
```
docker run lucacanali/test_cpu_parallel /opt/test_cpu_parallel -w 2
```


