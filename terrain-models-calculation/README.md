# Geospatial Use Case: WildfireRisk
WildfireRisk computes the models DSM, DEM, CHM, FCC, aspect and slope and generates plots of the execution time, cost and reading and writing throughput. The input data used are LAZ and LAS files.

## Configuration
### Lithops and IBM cloud
1. Create your Lithops configuration file, read the *Configuration file* section in [Lithops configuration](https://github.com/lithops-cloud/lithops/blob/master/config/README.md) to know where your file should be located.
2. Configure a [IBM Cloud Object Storage](https://github.com/lithops-cloud/lithops/blob/master/docs/source/storage_config/ibm_cos.md), it is recommended using the option 2 (COS HMAC credentials).

2. Configure a [IBM Cloud Functions](https://github.com/lithops-cloud/lithops/blob/master/docs/source/compute_config/ibm_cf.md). In addition to the basic configuration, it will be necessary to configure the `runtime_memory` to 2048 MB. 

    ```yaml
    ibm_cf:
        runtime_memory: 2048
     ```
   
3. Lithops has default runtimes, but none has all the required packages, so you have to create your runtime. In the directory [runtime](https://github.com/Sararl27/GeoSpatial_WildfireRisk/tree/main/runtime), there is the runtime you will need. To configure it, follow the steps in the *Custom runtime* section in [Lithops runtime for IBM Cloud Functions](https://github.com/lithops-cloud/lithops/blob/master/runtime/ibm_cf/README.md).

### WildfireRisk 
1. Configure your `LOCAL_INPUT_DIR` (the directory where is the data you want to upload), `DATA_BUCKET` (name of the storage bucket) and `INPUT_DATA_PREFIX` (the path where the data input will be stored in the cloud).

    ```python
    LOCAL_INPUT_DIR = '<PATH_INPUT_DATA>'                     # Example: 'data/'
    DATA_BUCKET = '<STORAGE_BUCKET>'                          # Example: 'objects-geospatial-wildfirerisk-test'
    INPUT_DATA_PREFIX = '<PATH_INPUT_DATA_STORAGE_BUCKET>'    # Example: 'data-example/'
    ```
