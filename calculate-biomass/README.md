# Cloudbutton Geospatial Use Case: Biomass Calculation
## Introduction
CalcBiomass is a Python project which allows us to calculate the vegetation biomass from LiDAR Data of a given area from some operations performed.

This notebook has been adapted from [the original pipeline](https://www.neonscience.org/resources/learning-hub/tutorials/calc-biomass-py) to be parallelized using serverless functions, thanks to the tool called [Lithops](https://github.com/lithops-cloud/lithops), which allows us to perform all the computation and storage of our process in the cloud in a safe and simple way. 

This way of working allows us to make a much faster and more efficient computation being able to obtain data on larger areas of the world in a shorter period of time.

## Requirements
* To have an a [runtime](https://github.com/lithops-cloud/lithops/tree/master/runtime) to use the libraries of the project.
* To have an [.asc](https://centrodedescargas.cnig.es/CentroDescargas/index.jsp) or geotiff file of the area to be scanned and processed.
* To have the file [SJER_Biomass_Training.csv](https://neondata.sharefile.com/share/view/cdc8242e24ad4517/fobd4959-4cf0-44ab-acc6-0695a04a1afc) to be able to carry out the training of our predictors.
* Have an account in one of the supported clouds.

## Additional resources
### Blogs
* [Lithops blog with all the information.](https://lithops-cloud.github.io/docs/)
* [Lithops supported clouds.](https://lithops-cloud.github.io/docs/source/configuration.html)
* [Original publication of the workflow.](https://www.neonscience.org/resources/learning-hub/tutorials/calc-biomass-py)