FROM continuumio/miniconda3:4.10.3

RUN echo "python==3.9.5" >> /opt/conda/conda-meta/pinned

ENV FLASK_PROXY_PORT 8080

RUN apt --allow-releaseinfo-change update \
    && apt upgrade -y --no-install-recommends \
    && apt install -y --no-install-recommends \
        gcc \
        libc-dev \
        libxslt-dev \
        libxml2-dev \
        libffi-dev \
        libssl-dev \
        zip \
        unzip \
        make \
    && rm -rf /var/lib/apt/lists/* \
    && apt-cache search linux-headers-generic

RUN conda update -n base conda && conda install -c conda-forge pdal python-pdal gdal && conda clean --all
RUN pip install --upgrade pip setuptools six wheel && pip install --no-cache-dir \
    # Lithops modules
    flask \
    pika \
    glob2 \
    ibm-cos-sdk \
    redis \
    gevent \
    requests \
    PyYAML \
    kubernetes \
    numpy \
    cloudpickle \
    ps-mem \
    tblib \
    # Geospatial modules
    pandas \
    scipy \
    Shapely \
    rasterio \
    sentinelsat \
    grass-session \
    rasterio \
    Fiona \
    rio-cogeo \
    joblib  \
    numpy \
    scikit-learn \
    pandas \
    geopandas \
    joblib \
    earthpy \
    packaging \
    cython

RUN mkdir -p /action \
    && mkdir -p /actionProxy \
    && mkdir -p /pythonAction

ADD https://raw.githubusercontent.com/apache/openwhisk-runtime-docker/8b2e205c39d84ed5ede6b1b08cccf314a2b13105/core/actionProxy/actionproxy.py /actionProxy/actionproxy.py
ADD https://raw.githubusercontent.com/apache/openwhisk-runtime-python/3%401.0.3/core/pythonAction/pythonrunner.py /pythonAction/pythonrunner.py

CMD ["/bin/bash", "-c", "cd /pythonAction && python -u pythonrunner.py"]
