#!/usr/bin/env python

from setuptools import setup, find_packages

description = "sparkhistogram contains helper functions for generating data histograms with the Spark DataFrame API and with Spark SQL."

long_description = "sparkhistogram contains helper functions for generating data histograms with the Spark DataFrame API and with Spark SQL."

setup(name='sparkhistogram',
    version='0.1',
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Luca Canali',
    author_email='luca.canali@cern.ch',
    url='https://github.com/LucaCanali/Miscellaneous/blob/master/Spark_Notes/Spark_DataFrame_Histograms.md',
    license='Apache License, Version 2.0',
    include_package_data=True,
    packages=find_packages(),
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
