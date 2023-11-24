#!/bin/bash

declare -a StringArray=("JDK/jdk8u392-b08" "JDK/jdk-11.0.21+9" "JDK/jdk-17.0.9+9" "JDK/jdk-17.0.9" "JDK/graalvm-jdk-17.0.9+11.1" )

for JDK in ${StringArray[@]}; 
do
   echo "Testing with:" $JDK
   export JAVA_HOME="/var/spark/"$JDK
   ./test_Spark_CPU_memory.py --num_workers 20 --sparkmeasure_path spark-measure_2.12-0.23.jar
   sleep 120
done

