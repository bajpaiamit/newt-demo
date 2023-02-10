from util.google.storage import get_config, list_blobs, copy_blob, get_bucket, get_blob
from util.google.pubsub import get_message, publish_message
from util.google.bigquery import get_job_config, create_table, get_table, query_table, load_table_from_uri
from util.utility import init_logger, get_metadata_query, log_rows

import re
from datetime import datetime, timedelta
import json

from flask import Flask, request
import traceback


task = "gcs_to_bq"
app = Flask(__name__)

logger = init_logger(task)

CONF_KEY = task

today_fmt = datetime.utcnow().strftime("%Y-%m-%d")
yesterday_fmt = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")


def table_schema(bucket, file_name):
    blobs = list_blobs(bucket, prefix="table_schema/")
    data = {}
    for blob in blobs:
        if file_name in blob.name:
            data = json.loads(blob.download_as_string())

    if data == {}:
        raise f"No Schema found for {file_name}"

    return data


@app.route("/", methods=["POST"])
def gcs_to_bq():

    try:
        blob = None
        bq_table_id = None
        envelope = request.get_json()
        data = get_message(envelope)

        yesterday_fmt = data.get('date')

        if yesterday_fmt is None:
            yesterday_fmt = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

        conf_path = data['conf_path']
        file_path = data['file_path']

        config = get_config(conf_path, CONF_KEY)
        input_bucket = config['input_bucket']
        project_id = config["project_id"]
        staging_dataset = config["staging_dataset"]
        ods_dataset = config["ods_dataset"]

        next_topic = config.get("next_topic")
        metadata_schema = table_schema(input_bucket, "Metadata_column.json")

        bucket = get_bucket(input_bucket)
        blob = get_blob(bucket, file_path)

        with blob.open() as fp:
            row_cnt = len(fp.readlines())
            logger.log_text(f"blob name and x {blob.name} - {str(row_cnt)}")

        uri = f"gs://{input_bucket}/{blob.name}"
        #_df = read_csv(uri)
        blob_name_schema = blob.name.split(".")[0] + ".json"
        logger.log_text(f"Blob Name Schema : " + str(blob_name_schema))
        blob_name_file = blob_name_schema.split("/")[3]
        schema = table_schema(input_bucket, blob_name_file)
        logger.log_text(f"schema " + str(schema))

        job_config = get_job_config(schema)
        csv_filename = re.findall(r".*/(.*).csv", blob.name)  # Extracting file name for BQ's table id
        table_name = f"Nexidia_{csv_filename[0]}"
        logger.log_text(f"table Name {table_name}")
        bq_table_id = f"{project_id}.{staging_dataset}.{table_name}"  # Determining table name

        log_rows(project_id, staging_dataset, table_name, logger)

        #df = standardize_and_reformat(_df, schema)
        #logger.log_text(f"First 10 lines of the dataframe:\n{df.head(10)}")
        #df_schema = df.dtypes.to_dict()
        #logger.log_text(f"dataframe schema {df_schema}")

        table = get_table(bq_table_id)

        if table is None:
            create_table(bq_table_id, schema)

        #job = load_table_from_df(df, bq_table_id, job_config=job_config)
        job = load_table_from_uri(uri, bq_table_id, job_config=job_config)
        #load_table_from_df(df, project_id, staging_dataset, table_name, schema)
        job.result()  # Waits for the job to complete.

        if row_cnt == 1:
            logger.log_text(f"File {uri} has 0 rows, no further action needed.")

        else:

            log_rows(project_id, staging_dataset, table_name, logger)
            logger.log_text(f"File {uri} uploaded.")
            # Check if the semantic table already exists

            bq_table_id_ods = f"{project_id}.{ods_dataset}.{table_name}"

            ods_table = get_table(bq_table_id_ods)

            if ods_table is not None:
                logger.log_text(f'Table {table_name} already exists in dataset {ods_dataset}.',
                                severity="INFO")
            else:

                for i in metadata_schema:
                    schema.append(i)
                create_table(bq_table_id_ods, schema)
                logger.log_text(f"Table {table_name} created in dataset {ods_dataset}.")

            log_rows(project_id, ods_dataset, table_name, logger)

            meta_data_query = get_metadata_query(bq_table_id, bq_table_id_ods, task)

            query_table(meta_data_query)

            log_rows(project_id, ods_dataset, table_name, logger)
            logger.log_text(f"Data inserted into the {bq_table_id_ods}")

            if next_topic:
                data = {
                    "conf_path": conf_path,
                    "table_project": project_id,
                    "table_schema": staging_dataset,
                    "table_id": table_name
                }
                publish_message(project_id, next_topic, data)

        return 'Success', 200

    except Exception as e:  # If table is not found, upload it.
        destination_path = f"Uncompressed_folders/Error/{yesterday_fmt}/{file_path}"
        if blob is not None:
            copy_blob(blob, input_bucket, destination_path)
        err = traceback.format_exc()
        log_text = f"{err}"

        if bq_table_id is not None:
            log_text = f"Table ID: {bq_table_id} - {err}"

        logger.log_text(log_text, severity="ERROR")
        return f"error: {str(e)} ", 200
