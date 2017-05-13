# Goal:   
**Enable Spark jobs (executors) to access Kerberized resources**
  * distribute the Kerberos cache file from the driver/client machine
  * make this work in a Hadoop/YARN cluster 

Note: the problem this tries to solve is how to enable Spark jobs to access resources protected by direct
Kerberos authentication.  
Notably this does not apply to the use of HDFS in a Spark+Hadoop cluster, where a more scalable delegation token-based 
implementation is available.

  
# Recipe:
Tested on: Apache Spark 1.6, 2.0 and 2.1 + YARN/Hadoop 2.6.0 (CDH)

1. Use `kinit` to get the Kerberos TGT in the credential cache file
use `klist -l` to get the path of the credential cache file. A typical default path value is: /tmp/krb5cc_$UID

2. This is an optional step: set KRB5CCNAME on the client/driver machine. Example:  
`export KRB5CCNAME=/tmp/krb5cc_$UID`

3. Distribute the credential cache and set the KRB5CCNAME variable on the executors. 
Examples when using spark-submit/pyspark/spark-shell:  

```bash
spark-shell --master yarn --files $KRB5CCNAME#krbcache --conf spark.executorEnv.KRB5CCNAME='FILE:$PWD/krbcache'

pyspark --master yarn --files $KRB5CCNAME#krbcache --conf spark.executorEnv.KRB5CCNAME='FILE:$PWD/krbcache'
```
   
   
# Notes: 
    
* Strategy and techniques used:

  * Distribute the Kerberos credential cache from the driver/client to all YARN containers as a local copy
    * use the standard Spark functionality, using `--files <path>` (or `--conf spark.yarn.dist.files=<path>`)
  * Set the executors' environment variable KRB5CCNAME to point to a local copy of the Kerberos credential cache file
    * the non-standard point is that the actual PATH of the local copy of the credential cache can end up to be different 
   for different machines/executors/YARN containers
  * How to set the Spark executor environment variable with a path relative to YARN container root directory
    * use `'$PWD'` to prefix the path of the credential cache to address the location of the root of the YARN container
    * use standard Spark configuration options to set the environment variable KRB5CCNAME: `--conf spark.executorEnv.KRB5CCNAME=FILE:<PATH_to_credential_cache>`
    
* An alternative method to shipping the credentail cache using Spark's --files is to copy the credential cache to all nodes of the cluster using a given value for the path (for example /tmp/krb5cc_$UID) and then set KRB5CCNAME to the path value.
    
* instead of distributing the credential cache with `--files` you can use `--conf spark.yarn.dist.files=<path>`

* What is the advantage of shipping the credential cache to the executors, compared to shipping the keytab? The cache can only be used/renewed for a limited amount of time, so it offers less risk if "captured" and provides a more suitable solution for short-running jobs in a shared environment for example, which is the case of many Spark jobs in a YARN environment.

* What is the key finding of this note? The fact that `$PWD` is set to the YARN container root, which is generated at runtime. Use $PWD inside single quotes if you need to set environment variables relative to the container root address.

* You can adapt this method to setting other environment variables, that similarly to KRB5CCNAME in this example, may depend on a relative path based on the YARN root container path.
   
   
# Credits:
   
Author: Luca.Canali@cern.ch, April 2017  
This works includes contributions by: Zbigniew.Baranowski@cern.ch and Prasanth.Kothuri@cern.ch


