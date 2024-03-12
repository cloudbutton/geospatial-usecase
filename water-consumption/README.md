# Cloudbutton Geospatial Use Case: Water Consumption

This notebook contains a workflow that calculates water consumption from crops using the Penman-Monteith formula and interpolation rasters of temperature, wind, solar irradiance and humidity for a given day. Get input data from the Spanish [Instituto Nacional de Informacion Geográfica](https://centrodedescargas.cnig.es/CentroDescargas/index.jsp). This workflow only processes data from Región de Múrcia and the MDT05 data formats. Download them and put the images in the `input_DTMs` directory. You can use `.tif` format files.

## Requirements

    - An AWS Account
    - Lithops 3.1.0
    - Python3.10

## Instructions


To execute this notebook you need:

1. Clone the repository of [cloudbutton_geospatial](https://github.com/cloudbutton/geospatial-usecase/).
2. Build the conda environment described in [here](https://github.com/cloudbutton/geospatial-usecase/blob/main/INSTALL.md) and install also this [requirements](/water-consumption/runtime/requirements.txt). Make sure your Lithops version is 3.1.0. If it is not, you can run:
    ```bash
    $ pip install --upgrade lithops==3.1.0
    ```
3. Setup Lithops to work with [AWS Lambda](https://lithops-cloud.github.io/docs/source/compute_config/aws_lambda.html).
4. Deploy the AWS Lambda Lithops runtime prepared for this workflow usins [this Dockerfile](/water-consumption/runtime/aws_lambda.Dockerfile) stored in the runtime directory:
   ```bash
   $ lithops runtime build -f aws_lambda.Dockerfile cloudbutton-wc:01
   ```
   
   ```bash
   $ lithops runtime deploy cloudbutton-wc:01 --memory 2048
   ```
5. Run:
   ```bash
   $ python3 water-consumption.py
   ```
