# Three methods to feed Parquet data to TensorFlow, with Examples

- Read data into memory and feed it to TensorFlow 
- Use the Petastorm library
- Convert data to the TFRecord data format and process it with the tf.data API

## Read all data into memory and feed it to TensorFlow
This works by reading the data in memory into numpy arrays and passing those to TensorFlow. 
A few examples:
    - [Read Parquet using PySpark and feed data from memory to tf.keras](4.0c-Training-HLF-TF_Keras_PySpark_Parquet.ipynb)
    - [Read with Pandas](4.0c_bis-Training-HLF-TF_Keras_Pandas_Parquet.ipynb)
    - [Read with PyArrow](4.0c_tris-Training-HLF-TF_Keras_Pyarrow_Parquet.ipynb)

## Read Parquet files using Petastorm and feed them to TensorFlow
[Petastorm](https://github.com/uber/petastorm) is library that enables single machine or distributed training and
evaluation of deep learning models directly from datasets in Apache Parquet format.  
Example:
    - [Petastorm read Parquet and feeds it to TensorFLow](4.0d-Training-HLF-TF_Keras_Petastorm_Parquet.ipynb)

## Covert data to the TFRecord format 
- TFRecord is a native data format for TensorFlow. Once data is converted in TFRecord format it 
  can be processed using tf.data, natively in TensorFlow. Example:
    - [Particle classifier - High Level Features](https://github.com/cerndb/SparkDLTrigger/blob/master/Training_HLF_Classifier/4.0e-Training-HLF-TF_Keras_TFRecord.ipynb)
    - [Particle classifier - Inclusive with LSTM](https://github.com/cerndb/SparkDLTrigger/blob/master/Training_Inclusive_Classifier/4.3a-Training-InclusiveClassifier-LSTM-TF_Keras_TFRecord.ipynb)

- Examples of how to convert Parquet into TFRecord using Apache Spark
  - See [Note on Spark and TFRecord](../Spark_Notes/Spark_TFRecord_HowTo.md)