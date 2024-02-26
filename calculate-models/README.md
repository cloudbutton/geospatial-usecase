# Cloudbutton Geospatial Use Case: Model Calculation

This notebook contains a model calculation process that consumes laz files. You can download examples of las files in [here](https://www.icgc.cat/es/Descargas/Elevaciones/Datos-lidar).

## Requisites

    - An AWS Account
    - Lithops 3.1.0
    - Python 3.10
    - conda installed

## Instructions

To execute this notebook you need:

1. Clone the repository of [cloudbutton_geospatial](https://github.com/cloudbutton/geospatial-usecase/tree/main/cloudbutton_geospatial).
2. The conda environment required is described in described in [here](https://github.com/cloudbutton/geospatial-usecase/blob/main/INSTALL.md).

3. Setup Lithops to work with [AWS Lambda](https://lithops-cloud.github.io/docs/source/compute_config/aws_lambda.html).

4. Deploy the AWS Lambda Lithops runtime prepared for this workflow following [this instructions](https://github.com/lithops-cloud/lithops/tree/master/runtime/aws_lambda) using the Docker file `'aws_lambda.Dockerfile'` in the runtime directory:
   ```bash
   $ lithops runtime build -f Dockerfile cloudbutton-model-calculation:01
   ```
   
   ```bash
   $ lithops runtime deploy cloudbutton-model-calculation:01 --memory 4096
   ```

5. Follow the instructions in the notebook to execute the code.

6. You can download other laz files to create different models. You just need to put them in the `input-las-tiles` directory. In this repository we give an example file.
