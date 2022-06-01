FROM python:3.9-buster

RUN apt-get update && \
        apt-get upgrade -y && \
        apt-get install -y \
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

RUN ogrinfo --version

RUN gdal-config --version

RUN pip install --upgrade --no-cache-dir setuptools==58.0.2 pip

COPY requirements.txt requirements.txt
RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal && \
    export C_INCLUDE_PATH=/usr/include/gdal && \
    pip install --upgrade pip six && pip install --no-cache-dir -r requirements.txt

WORKDIR /root

RUN curl -sSL http://step.esa.int/thirdparties/sen2cor/2.9.0/Sen2Cor-02.09.00-Linux64.run -o Sen2Cor-02.09.00-Linux64.run && \
    chmod +x Sen2Cor-02.09.00-Linux64.run && \
    bash Sen2Cor-02.09.00-Linux64.run --target /opt/sen2cor && \
    rm Sen2Cor-02.09.00-Linux64.run

# Setting environment variables
ENV SEN2COR_PATH=/opt/sen2cor \
    SEN2COR_HOME=/home/user/sen2cor/2.9

ENV SEN2COR_BIN=$SEN2COR_PATH/lib/python2.7/site-packages/sen2cor \
    PATH=$SEN2COR_PATH/bin:${PATH} \
    LD_LIBRARY_PATH=$SEN2COR_PATH/lib:${LD_LIBRARY_PATH} \
    GDAL_DATA=$SEN2COR_PATH/share/gdal \
    GDAL_DRIVER_PATH=disable \
    LC_NUMERIC=C \
    PYTHONUNBUFFERED=1

# Copy Lithops proxy and lib to the container image.
ENV APP_HOME /lithops
WORKDIR $APP_HOME

COPY lithops_aws_batch.zip .
RUN unzip lithops_aws_batch.zip && rm lithops_aws_batch.zip

ENTRYPOINT python3 entry_point.py
