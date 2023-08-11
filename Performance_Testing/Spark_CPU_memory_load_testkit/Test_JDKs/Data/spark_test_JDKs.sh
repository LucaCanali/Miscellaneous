#!/bin/bash

declare -a StringArray=("openlogic-openjdk-8u372-b07-linux-x64" "openlogic-openjdk-11.0.19+7-linux-x64" "openlogic-openjdk-17.0.7+7-linux-x64" "jdk-17.0.8" "graalvm-jdk-17.0.8+9.1")

for JDK in ${StringArray[@]}; 
do
   echo "Testing with:" $JDK
   export JAVA_HOME="/var/spark/"$JDK
   ./test_Spark_CPU_memory.py --num_workers 20 --sparkmeasure_path spark-measure_2.12-0.23.jar
done

