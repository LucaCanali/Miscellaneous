package ch.cern.test

import org.apache.spark.sql._

/**
  * Test Spark using a Scala object
  * This will run the method main of the object testSparkScala
  * bin/spark-submit --class ch.cern.test.testSparkScala <path>/target/scala-2.12/testsparkscala_2.12-0.1.jar
  */
object testSparkScala {

  def main(args: Array[String]): Unit = {

    val spark = SparkSession.
      builder().
      appName("testSparkScala").
      getOrCreate()

    
    println("FizzBuzz example!")

    spark.sql("""
      select case
        when id % 15 = 0 then 'FizzBuzz'
        when id % 3 = 0 then 'Fizz'
        when id % 5 = 0 then 'Buzz'
        else cast(id as string)
        end as FizzBuzz
      from range(1,20)
      order by id""").show()

    println("End of the example")

    spark.stop()
  }
}
