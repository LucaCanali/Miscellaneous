# HowTo: Enable Spark executors to access Kerberized resources
The problem this solves is enabling Spark jobs to access resources protected by Kerberos authentication.      
This recipe allows to:
  * distribute the Kerberos credentials cache file from the driver to the executors
  * set the relevant environment variables in the executors processes
  * enable the use of Kerberos authentication for Spark executors in a Hadoop/YARN clusters 

Limitations:
   * this recipe does not apply to Kerberos authentication for HDFS in a Spark+Hadoop cluster.
 In that case a more scalable, delegation token-based, implementation is available.

  
# Recipe:
Tested on: Apache Spark 1.6, 2.0, 2.1, 2.2, 2.3 + YARN/Hadoop

- `kinit` to get the Kerberos TGT in the credential cache file if not already there.

- use `klist -l` to get the path of the credential cache file.  
Example:  
```
$ klist -l
Principal name                 Cache name
--------------                 ----------
luca@CERN.CH                 FILE:/tmp/krb5cc_1001_Ve9jN3
```

- Send the Kerberos credentials cache file to the Spark executors YARN containers and set
the KRB5CCNAME variable to point to the credential files. Examples:  
Pyspark (Python):
```bash
pyspark --master yarn --files <path_to_Kerbero_Cache_File>#krbcache --conf spark.executorEnv.KRB5CCNAME="FILE:krbcache"
# Example:
pyspark --master yarn --files /tmp/krb5cc_1001_Ve9jN3#krbcache --conf spark.executorEnv.KRB5CCNAME="FILE:krbcache"
```   
Spark-shell (Scala):
```bash
spark-shell --master yarn --files <path_to_Kerbero_Cache_File>#krbcache --conf spark.executorEnv.KRB5CCNAME="FILE:krbcache"
# Example:
spark-shell --master yarn --files /tmp/krb5cc_1001_Ve9jN3#krbcache --conf spark.executorEnv.KRB5CCNAME="FILE:krbcache"
```
   
# Notes: 
    
* If KRB5CCNAME is already set in your environment startup scripts, you can use it to get the path to the Kerberos cache, beware of 
handling the "FILE:" prefix

* Strategy and techniques used:

  * Distribute the Kerberos credential cache from the driver/client to all YARN containers as a local copy
    * use the standard Spark functionality, using `--files <path>` (or `--conf spark.yarn.dist.files=<path>`)
    * `#krbcache` suffix provides an alias to the file which is handy to use in this context
  * Set the executors' environment variable KRB5CCNAME to point to a local copy of the Kerberos credential cache file 
  that is distributed in the YARN containes for the Spark executors
  * How to set the Spark executor environment variable with a path relative to YARN container root directory
    * use Spark configuration to set the environment variable KRB5CCNAME as in: `--conf spark.executorEnv.KRB5CCNAME=FILE:<PATH_to_credential_cache>`
    * using `FILE:krbcache` appears to be working and pick the file in the working directory of the YARN container
    * another possibility is using `./` to prefix the path of the credential cache to address the location of the root of the YARN container 
    * another option is using `'$PWD'` as a prefix for the YARN container working directory. 
     Note the need of using of single quotes to avoid resolving $PWD locally. 
     Note also that this particular method does not seem to work well for Python/PySpark use cases.
    
* An alternative method to shipping the credential cache using Spark command line option "--files", is to copy the 
credential cache to all nodes of the cluster using a given value for the path (for example /tmp/krb5cc_$UID) and then set KRB5CCNAME to the path value.
    
* An alternative syntax for distributing the credentials to the YARN containers instead of using `--files` from the command line is 
 to explicitly set the configuration parameter: `--conf spark.yarn.dist.files=<path>`

* What is the advantage of shipping the credential cache to the executors, compared to shipping the keytab? 
The cache can only be used/renewed for a limited amount of time, so it offers less risk if "captured" and provides a more suitable solution for short-running jobs in a shared environment for example, which is the case of many Spark jobs in a YARN environment.

* What are the key findings in this note? 
   * When using YARN/Hadoop, Spark executors have their working directory set to the YARN container 
   directory 
   * That Spark executors working directory is also where the "shipped" via `--files` are located
   * You can set relevant environment variables, for example KRB5CCNAME, to point to the files shipped 
   to executor's containers. If you need an absolute path, use the `$PWD` prefix. 

* You can adapt this method to setting other environment variables that, similarly to KRB5CCNAME in this example, may depend on a relative path based on the YARN root container path.
   
   
# Credits:
   
Author: Luca.Canali@cern.ch, April 2017, last updated on April 2018  
This work includes contributions by: Zbigniew.Baranowski@cern.ch and Prasanth.Kothuri@cern.ch


