# Apache Spark ecosystem:

Spark runs on top of Hadoop YARN, Apache Mesos standalone or in the cloud.
It is designed to work on large distributed clusters, but can also run on single machine.

Spark Core API is the fundation of the Apache Spark Ecosystem. It consists of:
- Spark SQL and data frames
  Spark SQL can act as a distributed SQL query engine. It creates DataFrame programming abstraction for data analysis.
- streaming (for real time data)
- MLlib (machine learning)
  The computation is completed in memory, so it is faster than Mapreduce.
- GraphX (graph-structured data at scale)
  directed multigraph (social networks)


Spark Core contains the basic functionalities of spark:
- task scheduling
- memory management
- Fault recovery
- interacting with storage systems

# Why PySpark?

PySpark the a python wrapper for spark.

Hadoop composed of closely integrated systems (Mapreduce for compute and HDFS for storage) so that it is hard to run one without the other.
Spark can be used on Hadoop storage or public cloud environment.

Spark can process data in memory, whereas Hadoop Mapreduce has do read from and write to disk.

Dask: parallel computing package in python and only support python (does not support SQL)

# Spark origins and Databricks:
Spark starts in 2009 as a research project in amplab at UC Berkeley.
It was designed to be fast for iteractive queries and iterative algorithms.
- in-memory storage
- efficient fault recovery

Paper: Spark: Cluster Computing with Working Sets

# Spark components:
- Driver program (SparkContext)
  respond to users programs or input and distributes and schedule work across the executors.
- Cluster Manager
  grant resources to applications
- Executor

Driver and Executors can run on one machine or different nodes of cluster.

![image](https://github.com/NxNiki/linked_course_apache_pyspark/assets/4017256/39172a94-0fa6-4237-ac75-bb1f20fb4d7c)


creating a spark session:
with spark 2.0, a spark session can access all the Spark's functionality through a single, unified point of entry.
when a spark session is started in Python, PySpark uses PY4G to launch a Java virtual machine and create a Java Spark context.
PY4G allows Python programs to dynamically access Java objects in a Java virtual machine.


# Partitions, transformations, lazy evaluations, and actions:

Partition is a collection of rows in the data frame that sits on one machine in a cluster.

Transformations: the instructions we use to modify the data frame. Spark does not act on transformations until we perform actions.

Lazy evaluation, when an operation is worked on your data, spark doesn't work on modifying the data straight away, it builds a plan of transformations that will be performed.
This allows Spark to create a streamlined plan and run efficiently across the cluster.

Action tells spark to compute the results of transformations:
- View data .show()
- Collection data .collect()
- Write data to output sources .write.format(...)





