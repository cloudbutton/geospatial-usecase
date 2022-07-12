# Cloudbutton Geospatial Use Case: Water Consumption

This notebook contains workflow that calculates water consumption from crops using the Penman-Monteith formula and interpolation rasters of temperature, wind, solar irradiance and humidity for a given day.

## Instructions

To execute this notebook you need:

1. An IBM Cloud account.
2. Setup Lithops to work with [IBM Cloud Functions](https://lithops-cloud.github.io/docs/source/compute_config/ibm_cf.html).
3. Deploy the IBM Cloud Functions Lithops runtime prepared for this workflow following [this instructions](https://github.com/lithops-cloud/lithops/tree/master/runtime/ibm_cf).
4. Get input data from the Spanish [Instituto Nacional de Informacion Geográfica](https://centrodedescargas.cnig.es/CentroDescargas/index.jsp). This workflow only processes data from Región de Múrcia and the MDT05 data formats. Download them and put the images in the `input_DTMs` directory. 
5. Follow the instructions in the notebook to execute the code.
