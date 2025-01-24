# How to create and use a docker image for running test_cpu_parallel

This guide explains how to create a Docker image for `test_cpu_parallel`, a CPU load testing
tool written in Rust.

- Before building the container image, you need to have the `test_cpu_parallel` binary executable for Linux in the same directory as your `Dockerfile`. 
  You can do this in one of two ways:
  - Option 1, build from source and copy the executable in this directory
    - See details of how to build in the [Code_test_CPU_Rust](../Code_test_CPU_Rust) folder
  - Option 2, download the binary executable from this link:
    ```
    wget https://sparkdltrigger.web.cern.ch/sparkdltrigger/test_cpu_parallel/test_cpu_parallel
    chmod +x test_cpu_parallel
    
    # Checksum:
    # sha256sum test_cpu_parallel
    # 6feabf4c59765e463e65e7150cd5636063af9d946ab56b8b5b45151b712d27e2
    ```
- Build the docker image with:
```
docker build -t lucacanali/test_cpu_parallel:v1.2 .
docker push lucacanali/test_cpu_parallel:v1.2

docker tag lucacanali/test_cpu_parallel:v1.2 lucacanali/test_cpu_parallel:latest
docker push lucacanali/test_cpu_parallel:latest
```

## Using the container image

Once the container image is built or pulled from the registry, you can use it to run `test_cpu_parallel`:
```
docker run lucacanali/test_cpu_parallel /opt/test_cpu_parallel -w 2

podman run lucacanali/test_cpu_parallel /opt/test_cpu_parallel -w 2
```

## Kubernetes
You can run `test_cpu_parallel` on a Kubernetes cluster as in:
```
# delete pod if it already exists and start a new one with the test_cpu_parallely workload
kubectl get pod test-cpu-pod && kubectl delete pod test-cpu-pod
kubectl run test-cpu-pod --image=lucacanali/test_cpu_parallel --restart=Never -- /opt/test_cpu_parallel -w 2

# get the output
kubectl logs -f test-cpu-pod
```

Or you can use the [yaml file](test_cpu_parallel.yaml) to create a pod and run the test as in:
```
# delete pod if it already exists and start a new one with the test_CPU_parallel.py workload
kubectl get pod test-cpu-pod && kubectl delete pod test-cpu-pod
kubectl apply -f test_cpu_parallel.yaml

# get the output
kubectl logs -f test-cpu-pod
```
