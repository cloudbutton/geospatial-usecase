# Installation instructions

1. [Install anaconda](https://docs.anaconda.com/anaconda/install/linux/)

2. Create a new conda environment:
```
(base) $ conda create --name geospatial python=3.9
```

3. Activate geospatial environment:
```
(base) $ conda activate geospatial
```

4. Install python dependencies:
```
(geospatial) $ pip install -r requirements.txt
```

5. Install conda dependencies:
```
(geospatial) $ conda install -c conda-forge ipywidgets ipyleaflet pdal python-pdal gdal
```

6. Install conda kernel for jupyter lab:
```
(geospatial) $ ipython kernel install --user --name=cloudbutton-geospatial
```

7. Start jupyter lab:
```
(geospatial) $ jupyter lab
```

8. Select the geospatial environment kernel created:
![jupyter kernel selection](.images/install-jupyter.png)
