# Cloudbutton Geospatial Use Case: Sentinel2 image pre-processing

This notebook contains a process that downloads Sentinel2 images and applies atmospheric correction. Finally, the are transformed to Cloud-Optimized GeoTIFF to enable massive parallel processing using serverless functions consuming images from Object Storage.

## Instructions

To execute this notebook you need:

1. An AWS Account.
2. Setup Lithops to work with [AWS Batch](https://lithops-cloud.github.io/docs/source/compute_config/aws_batch.html).
3. Deploy the AWS Batch Lithops runtime prepared for this workflow following [this instructions](https://github.com/lithops-cloud/lithops/tree/master/runtime/aws_lambda).
4. Create an account in the [Copernicus Open Data Hub](https://scihub.copernicus.eu/).
5. Follow the instructions in the notebook to execute the code.
