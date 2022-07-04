# Geospatial Use Case: Lidar Partitioner
Lidar Partitioner splits the file into several other files/partitions according to density. All the resulting files will have a similar size, since they have a similar amount of points. A buffer is also stores to improve results during later processing.

## Configuration
### Lithops and IBM cloud
1. Create your Lithops configuration file, read the *Configuration file* section in [Lithops configuration](https://github.com/lithops-cloud/lithops/blob/master/config/README.md) to know where your file should be located.
2. Configure a [IBM Cloud Object Storage](https://github.com/lithops-cloud/lithops/blob/master/docs/source/storage_config/ibm_cos.md), it is recommended using the option 2 (COS HMAC credentials).
3. Configure a [IBM Cloud Functions](https://github.com/lithops-cloud/lithops/blob/master/docs/source/compute_config/ibm_cf.md). In addition to the basic configuration, it will be necessary to configure the `runtime_memory` to 2048 MB. 

    ```yaml
    ibm_cf:
        runtime_memory: 2048
     ```

4. A runtime has been created and is currently working. In case this runtime stops working in the future, in the directory [runtime](https://github.com/ArnauGabrielAtienza/geospatial-usecase/tree/partitioner/lidar-partitioner-cloud-performance/runtime), you will find the configuration files needed. To configure it, follow the steps in the *Custom runtime* section in [Lithops runtime for IBM Cloud Functions](https://github.com/lithops-cloud/lithops/blob/master/runtime/ibm_cf/README.md).

### Lidar Partitioner
Two notebooks have been provided. [partitioner.ipynb](https://github.com/ArnauGabrielAtienza/geospatial-usecase/tree/partitioner/lidar-partitioner-cloud-performance/partitioner.ipynb) provides the code to test the performance of the partitioning process of our Lidar partitioner. [regional_partitioner](https://github.com/ArnauGabrielAtienza/geospatial-usecase/tree/partitioner/lidar-partitioner-cloud-performance/regional_partitioner.ipynb) tests the performance of the partitioning process of a sample sub-optimal partitioning process. Both of them use IBM_COS as Object Storage and IBM_CF as Backend.

In order to execute the notebooks with your own files you will need to change the following in the "Partitioning Variables" cell:

1. In the case of partitioner.ipynb:

	```python
   	bucketPath = '<Path to the files to be partitioned>'			# Example: 'cos://lithops-testing/Catalonia/'
   	bucketName = '<Name of the bucket>'					# Example: 'lithops-testing'
   	partition_size = '<Number of points in each partition>'			# Example: 500_000
   	buffer_size = '<Buffer size>'						# Example: 5
	```

2. In the case of regional_partitioner:

	```python
   	bucketPath = '<Path to the files to be partitioned>'			# Example: 'cos://lithops-testing/Catalonia/'
   	bucketName = '<Name of the bucket>'					# Example: 'lithops-testing'
	square_splits = '<Number of splits>'					# Example: 2
	```
