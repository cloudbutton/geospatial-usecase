# Cloudbutton Geospatial Use Case: NDVI Calculation

This notebook contains a NDVI calculation process that consumes Sentinel2 satellite image from the [AWS Sentinel2 open data repository](https://registry.opendata.aws/sentinel-2/).

## Requisites

- An AWS Account
- Lithops 2.9.0
- botocore 1.31.61
- conda environment described in [here](https://github.com/cloudbutton/geospatial-usecase/blob/main/INSTALL.md)

## Instructions

To execute this notebook you need:

1. Clone the repository of [cloudbutton_geospatial](https://github.com/cloudbutton/geospatial-usecase/tree/main/cloudbutton_geospatial).

2. Setup Lithops to work with [AWS Lambda](https://lithops-cloud.github.io/docs/source/compute_config/aws_lambda.html).

3. Deploy the AWS Lambda Lithops runtime prepared for this workflow following [this instructions](https://github.com/lithops-cloud/lithops/tree/master/runtime/aws_lambda) using the Docker file `'Dockerfile'` in the runtime directory:
   ```bash
   $ lithops runtime build -f Dockerfile cloudbutton-ndvi:01
   ```
   
   ```bash
   $ lithops runtime deploy cloudbutton-ndvi:01 --memory 4096
   ```
    
4. Follow the instructions in the notebook to execute the code using the cloudbutton-geospatial kernel.

5. In order to make sure to process some images you can use the default configuration with the default dates, 15 value for cloud cover and the california coordinates named `'cali_coord'`.

**Note:** you can modify the runtime name but then you will need to edit it in the corresponding cells too.
