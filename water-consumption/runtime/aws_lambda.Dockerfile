# Python 3.10
FROM python:3.10-slim-buster

RUN apt-get update \
    # Install aws-lambda-cpp build dependencies
    && apt-get install -y \
      g++ \
      make \
      cmake \
      unzip \
      build-essential \
      gcc \
      grass \
      grass-core \
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
ENV HOME=/tmp

ARG FUNCTION_DIR="/function"

# Copy function code
RUN mkdir -p ${FUNCTION_DIR}

# Update pip
RUN pip install --upgrade --ignore-installed pip wheel six setuptools \
    && pip install --upgrade --no-cache-dir --ignore-installed \
        awslambdaric \
        boto3 \
        redis \
        httplib2 \
        requests \
        numpy \
        scipy \
        pandas \
        pika \
        kafka-python \
        cloudpickle \
        ps-mem \
        tblib \
        fiona \
        grass-session \
        rasterio \
        psutil

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip six wheel setuptools && \
   pip install --no-cache-dir -r requirements.txt


# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Add Lithops
COPY lithops_lambda.zip ${FUNCTION_DIR}
RUN unzip lithops_lambda.zip \
    && rm lithops_lambda.zip \
    && mkdir handler \
    && touch handler/__init__.py \
    && mv entry_point.py handler/

# Put your dependencies here, using RUN pip install... or RUN apt install...

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "handler.entry_point.lambda_handler" ]
