FROM python:3.9-buster

RUN apt-get update && \
        apt-get upgrade -y && \
        apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        grass \
        grass-dev \        
        libc-dev \
        libxslt-dev \
        libxml2-dev \
        libffi-dev \
        libssl-dev \
        zip \
        unzip \
        vim \
        libgdal-dev \
        gdal-bin \
        && rm -rf /var/lib/apt/lists/* \
        && apt-cache search linux-headers-generic

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV GRASSBIN=grass76

COPY requirements.txt requirements.txt 

RUN pip install --upgrade pip six wheel setuptools && \
    pip install --no-cache-dir -r requirements.txt

ENV FLASK_PROXY_PORT 8080

CMD python3
