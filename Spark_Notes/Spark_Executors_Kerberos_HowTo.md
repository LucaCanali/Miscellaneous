# Goal: 
* **Enable Spark jobs (executors) to access Kerberized resources**
  * distribute the Kerberos cache file from the driver/client machine
  * make this work for a YARN cluster 

Note: the reason for doing this is to enable access to resource protected by direct Kerberos authentication, notably this does not apply to the use of HDFS in a Hadoop cluster, where a more scalable token-based implementation is available

Proposed strategy and notes:

* Distribute the Kerberos credential cache from the driver/client to all YARN containers
   * use the standard Spark functionatility, using `--files` (or `--conf spark.yarn.dist.files`)
* Set the executors' environment variable KRB5CCNAME to point to a local copy of the Kerberos credential cache file
   * the difficult point is that the actual PATH can be different for different machines and is computed at run time
* How to set the Spark executor environemnt variable 
   * use the standard Spark functionality: `--conf spark.executorEnv.KRB5CCNAME=FILE:<PATH_to_credential_cache>`
   * tip: use `'$PWD'` to prefix the path of the credential cache to address the location of the root of the YARN container
    
   
   
# Recipe:
Tested on Apache Spark 2.1.x and YARN/Hadoop 2.6.0

1. Use `kinit` to get the MIT Kerberos TGT in the credential cache file
use `klist -l` to get path of credential cache file. A typical default path vlaue is: /tmp/krb5cc_$UID

2. This is an optional step: set KRB5CCNAME on the client/driver machine. Example:  
`export KRB5CCNAME=/tmp/krb5cc_$UID`

3. Distribute the credential cache and set the KRB5CCNAME variable on the executors. Examples when using spark-submit/pyspark/spark-shell:  

```bash
spark-shell --master yarn --files $KRB5CCNAME#krbcache --conf spark.executorEnv.KRB5CCNAME='FILE:$PWD/krbcache'

pyspark --master yarn --files $KRB5CCNAME#krbcache --conf spark.executorEnv.KRB5CCNAME='FILE:$PWD/krbcache'
```

   
   
# Notes: 
    
* An alternative method to shipping the credentail cache using Spark's --files is to copy the credential cache to all nodes of the cluster using a given value for the path (for example /tmp/krb5cc_$UID) and then set KRB5CCNAME to the path value.
    
* instead of distributing the credential cache with `--files` you can use `--conf spark.yarn.dist.files=<path>`

* What is the advantage of shipping the credential cache to the executors, compared to shipping the keytab? The cache can only be used/renewed for a limited amount of time, so it offers less risk if "captured" and provides a more suitable solution for short-running jobs in a shared enviroment for example, which is the case of many Spark jobs in a YARN environment.

* What is the key finding of this note? The fact that `$PWD` is set to the YARN container root, which is generated at runtime. Use $PWD inside single quotes if you need to set environment variables relative to the container root address.

* You can adapt this method to setting other environment variables besides KRB5CCNAME that depend of a relative path based on YARN root container path.
   
   
# Credits:
   
Author: Luca.Canali@cern.ch, April 2017  
Additional credits: Zbigniew.Baranowski@cern.ch and Prasanth.Kothuri@cern.ch


