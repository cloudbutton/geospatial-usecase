# CalcBiomass
## Introduction
CalcBiomass is a Python project which allows us to calculate the vegetation biomass from LiDAR Data of a given area from some operations performed.

This project makes use of the tool called [Lithops](https://github.com/lithops-cloud/lithops), which allows us to perform all the computation and storage of our process in the cloud in a safe and simple way. 

This way of working allows us to make a much faster and more efficient computation being able to obtain data on larger areas of the world in a shorter period of time.

## Requirements
* To have an a [runtime](https://github.com/lithops-cloud/lithops/tree/master/runtime) to use the libraries of the project.
* To have an [.asc](https://centrodedescargas.cnig.es/CentroDescargas/index.jsp) or geotiff file of the area to be scanned and processed.
* To have the file [SJER_Biomass_Training.csv](https://neondata.sharefile.com/share/view/cdc8242e24ad4517/fobd4959-4cf0-44ab-acc6-0695a04a1afc) to be able to carry out the training of our predictors.
* Have an account in one of the supported clouds.


## Configuration:
Perform the necessary configuration for [Lithops](https://github.com/lithops-cloud/lithops/tree/master/config) and enter the BUCKET_NAME field the name of your bucket. This will allow us to store and manage the data during the execution.

## Additional resources
### Blogs
* [Lithops blog with all the information.](https://lithops-cloud.github.io/docs/)
* [Original explanation of the workflow.](https://www.neonscience.org/resources/learning-hub/tutorials/calc-biomass-py)