# Container image for test_CPU_parallel.py
# A basic CPU workload generator
# See: https://github.com/LucaCanali/Miscellaneous/tree/master/Performance_Testing/Test_CPU_parallel_Python

ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-alpine

LABEL org.opencontainers.image.title="test_CPU_parallel"
LABEL org.opencontainers.image.description="Container image for the test_CPU_parallel Python CPU workload generator"
LABEL org.opencontainers.image.source="https://github.com/LucaCanali/Miscellaneous/tree/master/Performance_Testing/Test_CPU_parallel_Python"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir test_CPU_parallel

CMD ["test_CPU_parallel.py"]

