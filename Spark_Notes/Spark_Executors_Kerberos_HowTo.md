# HowTo: Enable Spark executors to access Kerberized resources
This recipe allows to:
  * distribute the Kerberos credentials cache file from the driver to the executors
  * set the relevant environment variables in the executors processes
  * enable the use of Kerberos authentication for Spark executors in a Hadoop/YARN clusters 

The problem this solves is enabling Spark jobs to access resources protected by Kerberos authentication.      

Note: this recipe does not apply to Kerberos authentication for HDFS in a Spark+Hadoop cluster.
 In that case a more scalable, delegation token-based, implementation is available.

  
# Recipe:
Tested on: Apache Spark 1.6, 2.0, 2.1, 2.2 + YARN/Hadoop

0. Optional step: set KRB5CCNAME on the client/driver. Note: use `klist -l` to get the path of the credential cache file. 
Example:  
`export KRB5CCNAME=/tmp/krb5cc_$UID`  

1. `kinit` to get the Kerberos TGT in the credential cache file if not already there.

2. Distribute the executors the credential cache file and set the KRB5CCNAME variable. Examples:

```bash
spark-shell --master yarn --files $KRB5CCNAME#krbcache --conf spark.executorEnv.KRB5CCNAME='FILE:krbcache'

pyspark --master yarn --files $KRB5CCNAME#krbcache --conf spark.executorEnv.KRB5CCNAME='FILE:krbcache'
```
   
   
# Notes: 
    
* Strategy and techniques used:

  * Distribute the Kerberos credential cache from the driver/client to all YARN containers as a local copy
    * use the standard Spark functionality, using `--files <path>` (or `--conf spark.yarn.dist.files=<path>`)
  * Set the executors' environment variable KRB5CCNAME to point to a local copy of the Kerberos credential cache file
    * the non-standard point is that the actual PATH of the local copy of the credential cache can end up to be different 
   for different machines/executors/YARN containers
  * How to set the Spark executor environment variable with a path relative to YARN container root directory
    * use Spark configuration options to set the environment variable KRB5CCNAME: `--conf spark.executorEnv.KRB5CCNAME=FILE:<PATH_to_credential_cache>`
    * using `FILE:krbcache` appears to be working and pick the file in the working directory of the YARN container
    * another possibility is using `./` to prefix the path of the credential cache to address the location of the root of the YARN container 
    * using `'$PWD'` as a prefix for the YARN container root is also possible however does not seem to work for Pythons/PySpark use cases
    
* An alternative method to shipping the credential cache using Spark command line option "--files", is to copy the credential cache to all nodes of the cluster using a given value for the path (for example /tmp/krb5cc_$UID) and then set KRB5CCNAME to the path value.
    
* An alternative syntax for distributing the credentials to the YARN containers instead of using `--files` from the command line is 
 to explicitly set the configuration parameter: `--conf spark.yarn.dist.files=<path>`

* What is the advantage of shipping the credential cache to the executors, compared to shipping the keytab? 
The cache can only be used/renewed for a limited amount of time, so it offers less risk if "captured" and provides a more suitable solution for short-running jobs in a shared environment for example, which is the case of many Spark jobs in a YARN environment.

* What are the key points of this note? 
The fact that Spark executors have their working directory set to the YARN container root, which is also
the destination of files "shipped" via --files and that we can set the relevant environment varialble, KRB5CCNAME
to point to the credential files in the working directory of the YARN container.

* You can adapt this method to setting other environment variables that, similarly to KRB5CCNAME in this example, may depend on a relative path based on the YARN root container path.
   
   
# Credits:
   
Author: Luca.Canali@cern.ch, April 2017 + updated February 2018  
This work includes contributions by: Zbigniew.Baranowski@cern.ch and Prasanth.Kothuri@cern.ch


