ARG build_env=testing
# start by pulling the python image
FROM python:3.8.15-slim-bullseye as base


ARG build_env
ENV APP_HOME /app
# switch working directory
WORKDIR $APP_HOME
COPY $build_env/ ./
COPY requirements.txt requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt && mkdir util util/google

COPY util/ ./util

# install the dependencies and packages in the requirements file
FROM base AS branch_sftp_extract

FROM base AS branch_sftp_file_extractor

FROM base AS branch_sftp_file_process

FROM base AS branch_decrypt_and_extract
ARG build_env
RUN if [ "$build_env" = "decrypt_and_extract" ]; \
    then chmod 755 decrypt_and_extract.sh && apt-get update -y && apt-get upgrade -y && apt-get install gpg unzip curl libcurl4-openssl-dev -y && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | \ 
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && apt-get update -y && apt-get install google-cloud-cli -y; \
    fi


FROM base AS branch_dlp_data_catalog

FROM base AS branch_tag_results

FROM base AS branch_gcs_to_bq

ARG build_env
FROM branch_${build_env}
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app

