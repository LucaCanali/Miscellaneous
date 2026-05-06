# Build and run a Docker image for `test_CPU_parallel.py`

This directory contains the files needed to build a container image for
`test_CPU_parallel.py`, a simple Python CPU load-testing tool.

Project source:

https://github.com/LucaCanali/Miscellaneous/tree/master/Performance_Testing/Test_CPU_parallel_Python

## Build the image

Build the image for Python 3.13:

```bash
docker build \
  --build-arg PYTHON_VERSION=3.13 \
  -t lucacanali/test_cpu_parallel.py:py3.13 \
  .
```

Push the image:

```bash
docker push lucacanali/test_cpu_parallel.py:py3.13
```

Optionally tag it as `latest`:

```bash
docker tag lucacanali/test_cpu_parallel.py:py3.13 lucacanali/test_cpu_parallel.py:latest
docker push lucacanali/test_cpu_parallel.py:latest
```

## Available image tags

Example tags:

```text
lucacanali/test_cpu_parallel.py:py3.12
lucacanali/test_cpu_parallel.py:py3.13
lucacanali/test_cpu_parallel.py:latest
```

## Run with Docker

Run the workload with two parallel workers:

```bash
docker run --rm lucacanali/test_cpu_parallel.py:py3.13 test_CPU_parallel.py -w 2
```

The number of parallel workers can be configured with the `-w` option.

To display the command help:

```bash
docker run --rm lucacanali/test_cpu_parallel.py:py3.13 test_CPU_parallel.py --help
```

## Run on Kubernetes

Create a test pod:

```bash
kubectl delete pod test-cpu-pod --ignore-not-found

kubectl run test-cpu-pod \
  --image=lucacanali/test_cpu_parallel.py:py3.13 \
  --restart=Never \
  -- test_CPU_parallel.py -w 2
```

Follow the logs:

```bash
kubectl logs -f test-cpu-pod
```

Delete the pod when finished:

```bash
kubectl delete pod test-cpu-pod
```

## Run on Kubernetes with YAML

You can also use the provided Kubernetes manifest:

```bash
kubectl delete pod test-cpu-pod --ignore-not-found
kubectl apply -f test_CPU_parallel.yaml
kubectl logs -f test-cpu-pod
```
