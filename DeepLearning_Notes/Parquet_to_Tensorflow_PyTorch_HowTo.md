# Three methods to feed Parquet data into TensorFlow or PyTorch
This note documents three easy methods to help you get started with data pipelines for TensorFlow or PyTorch.
For simplicity, we assume the data source to be Apache Parquet files, but this can be easily extended to other data formats.    
Choose one of these methods, as it best fits your problem:

1. Load data into memory and feed it to TensorFlow or Pytorch 
2. Use the Petastorm library to load Parquet and feed it to TensorFlow or Pytorch
3. Convert data to the TFRecord data format and process it natively using TensorFlow

## 1. Load data into memory then feed it to TensorFlow or Pytorch
This works by reading the data in memory using Pandas or similar packages, convert it into numpy arrays
and then passing those to TensorFlow.  
Examples:  
    - [Read with Pandas and feed to TensorFlow](https://github.com/cerndb/SparkDLTrigger/blob/master/Training_HLF_Classifier/4.0c_bis-Training-HLF-TF_Keras_Pandas_Parquet.ipynb)  
    - [Read with Pandas and feed to PyTorch](https://github.com/cerndb/SparkDLTrigger/blob/master/Training_HLF_Classifier/4.0g-Training-HLF-PyTorch_Pandas_Parquet.ipynb)  
    - [Read using PySpark and feed data from memory to TensorFlow](https://github.com/cerndb/SparkDLTrigger/blob/master/Training_HLF_Classifier/4.0c-Training-HLF-TF_Keras_PySpark_Parquet.ipynb)    
    - [Read with PyArrow and feed to TensorFlow](https://github.com/cerndb/SparkDLTrigger/blob/master/Training_HLF_Classifier/4.0c_tris-Training-HLF-TF_Keras_Pyarrow_Parquet.ipynb) 

## 2. Ingest Parquet files using Petastorm and feed them to TensorFlow or Pytorch
[Petastorm](https://github.com/uber/petastorm) is library that enables single machine or distributed training and
evaluation of deep learning models directly from datasets in Apache Parquet format.    
Examples:  
    - [Petastorm + TensorFlow for the HLF classifier](https://github.com/cerndb/SparkDLTrigger/blob/master/Training_HLF_Classifier/4.0d-Training-HLF-TF_Keras_Petastorm_Parquet.ipynb)    
    - [Petastorm + PyTorch for the HLF classifier](https://github.com/cerndb/SparkDLTrigger/blob/master/Training_HLF_Classifier/4.0h-Training-HLF-PyTorch_Petastorm_Parquet.ipynb)  
    - [**Large Dataset:** Petastorm + TensorFLow for the Inclusive classifier](https://github.com/cerndb/SparkDLTrigger/blob/master/Training_HLF_Classifier/4.0d-Training-HLF-TF_Keras_Petastorm_Parquet.ipynb)  

## 3. Covert data into the TFRecord format and ingest the datasets natively with TensorFlow
TFRecord is a native data format for TensorFlow. Once data is converted in TFRecord format it 
can be processed natively in TensorFlow using tf.data and tf.io.  
Examples:  
    - [Particle classifier - High Level Features, data in TFRecord format](https://github.com/cerndb/SparkDLTrigger/blob/master/Training_HLF_Classifier/4.0e-Training-HLF-TF_Keras_TFRecord.ipynb)  
    - [**Large Dataset:** Particle classifier - Inclusive with LSTM, data in TFRecord format](https://github.com/cerndb/SparkDLTrigger/blob/master/Training_Inclusive_Classifier/4.3a-Training-InclusiveClassifier-LSTM-TF_Keras_TFRecord.ipynb)    

### Examples of how to convert Parquet files into TFRecord using Apache Spark
  - See [Note on using Spark to process data in TFRecord format](../Spark_Notes/Spark_TFRecord_HowTo.md)  
