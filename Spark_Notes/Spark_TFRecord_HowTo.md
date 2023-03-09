## How to convert data into TFRecords format using Spark
This solution is about converting data into TFRecord, which is a format that Tensorflow can read natively.

For Spark 3.x there is not a maven central package yet (as of February 2023), but you can compile the jar from GitHub:

```
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk
export PATH=/usr/lib/jvm/java-1.8.0-openjdk/bin/:$PATH
mvn clean package
```

Use it with Spark: `--jars spark-tensorflow-connector_2.12-1.11.0.jar`
For convenience, I have uploaded the jar to a website, you can use it as follows:

```
# Build from source or use the pre-compiled JARs
# Stopgap, file served from my homepage
JAR=http://canali.web.cern.ch/res/spark-tensorflow-connector_2.12-1.11.0.jar

# start pyspark or spark-shell or spark-submit with the tensorflow connector jar
bin/pyspark --jars $JAR

# read a parquet file and save it in tfrecord format
df = spark.read.parquet(inputPath + "myfile.parquet")
numPartitions = 1
df.coalesce(numPartitions).write.format("tfrecords").save(outputPath+"myfile.tfrecord")
```

For Spark 2.x, the package is available on maven central:
`bin/spark-shell --packages org.tensorflow:spark-tensorflow-connector_2.11:1.14.0`

### Examples of dataset preparation with TFRecord

- [Convert the full dataset to TFRecord format](https://github.com/cerndb/SparkDLTrigger/blob/master/Datasets_Final_Preparation/DataPrep_extract_and_convert_Full_Dataset_TFRecord.ipynb)
- [Convert the High Level Features dataset to TFRecord](https://github.com/cerndb/SparkDLTrigger/blob/master/Datasets_Final_Preparation/DataPrep_convert_HLF_Dataset_TFRecord.ipynb)

### Tensorflow and tf.data
This is an example of how you can read data in TFRecord format with TensorFlow using the 
tf.data API

```
# Read the training dataset 
folder = PATH + "trainUndersampled_HLF_features.tfrecord"
files_train_dataset = tf.data.Dataset.list_files(folder + "/part-r*", seed=4242)
train_dataset=tf.data.TFRecordDataset(files_train_dataset)

# Function to decode TF records into the required features and labels
def decode(serialized_example):
    deser_features = tf.io.parse_single_example(
      serialized_example,
      # Defaults are not specified since both keys are required.
      features={
          'encoded_label': tf.io.FixedLenFeature((3), tf.float32),
          'HLF_input': tf.io.FixedLenFeature((14), tf.float32),
          })
    return(deser_features['HLF_input'], deser_features['encoded_label'])

parsed_train_dataset=train_dataset.map(decode, num_parallel_calls=tf.data.experimental.AUTOTUNE)
```

See some real-life examples from the repo [SparkDLTrigger](https://github.com/cerndb/SparkDLTrigger) at:
  - [Particle classifier - High Level Features](https://github.com/cerndb/SparkDLTrigger/blob/master/Training_HLF_Classifier/4.0e-Training-HLF-TF_Keras_TFRecord.ipynb)
  - [Particle classifier - Inclusive with LSTM](https://github.com/cerndb/SparkDLTrigger/blob/master/Training_Inclusive_Classifier/4.3a-Training-InclusiveClassifier-LSTM-TF_Keras_TFRecord.ipynb)
 
