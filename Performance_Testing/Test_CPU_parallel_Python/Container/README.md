# How to create and use a docker image for running test_CPU_parallel.py

This creates a docker image for test_CPU_parallel.py, a CPU load testing tool written in Python.  

- Link or copy the test_CPU_parallel binary executable for Linux to this directory
    ```
    ln -s ../test_CPU_parallel/test_CPU_parallel.py .
    ```
- Build the docker image with:
```
docker build -t lucacanali/test_cpu_parallel.py:py3.11 -f Dockerfile_Python3.11 .
docker push lucacanali/test_cpu_parallel.py:py3.11

# optional, tag as latest
docker tag lucacanali/test_cpu_parallel.py:py3.11 lucacanali/test_cpu_parallel.py:latest
docker push lucacanali/test_cpu_parallel.py:latest
```

## Docker
You can use the image to run test_CPU_parallel in a container as in:
```
docker run lucacanali/test_cpu_parallel.py:py3.11 test_CPU_parallel.py -w 2
```

You can choose the number of workers to run in parallel with the `-w` option, see also the help for test_CPU_parallel.py  
Multiple images are available for different versions of Python, see the [Dockerfile](Dockerfile) for details: 
`lucacanali/test_cpu_parallel.py:py3.11`, `lucacanali/test_cpu_parallel.py:py3.10`, `lucacanali/test_cpu_parallel.py:py3.9`

## Kubernetes
You can run test_CPU_parallel.py on a Kubernetes cluster as in:
```
# delete pod if it already exists and start a new one with the test_CPU_parallel.py workload
kubectl get pod test-cpu-pod && kubectl delete pod test-cpu-pod
kubectl run test-cpu-pod --image=lucacanali/test_cpu_parallel.py:py3.11 --restart=Never -- test_CPU_parallel.py -w 2

# get the output
kubectl logs -f test-cpu-pod
```

Or you can use the [yaml file](test_CPU_parallel.yaml) to create a pod and run the test as in:
```
# delete pod if it already exists and start a new one with the test_CPU_parallel.py workload
kubectl get pod test-cpu-pod && kubectl delete pod test-cpu-pod
kubectl apply -f test_CPU_parallel.yaml

# get the output
kubectl logs -f test-cpu-pod
```
