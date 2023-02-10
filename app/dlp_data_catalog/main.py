
from util.google.storage import get_config
from util.google.pubsub import publish_message, get_message
from util.google.bigquery import query_table
from util.google.datacatalog import get_info_types
from util.google.dlp import create_dlp_job, get_inspect_config, get_big_query_storage_options, get_storage_config,\
    create_save_finding_action

from datetime import datetime, timedelta
from flask import Flask, request
import traceback

from util.utility import init_logger

app = Flask(__name__)

task = "dlp_data_catalog"
logger = init_logger(task)

CONF_KEY = task

yesterday_fmt = (datetime.utcnow()-timedelta(days=1)).strftime("%Y-%m-%d")


@app.route("/", methods=["POST"])
def dlp_job():

    try:

        envelope = request.get_json()
        data = get_message(envelope)

        conf_path = data['conf_path']
        table_project = data['table_project']
        table_schema = data['table_schema']
        table_id = data['table_id']

        config = get_config(conf_path, CONF_KEY)

        project_id = config["project_id"]
        location = config["location"]
        _info_types = config.get("info_types")

        next_topic = config.get("next_topic")

        min_likelihood = config['min_likelihood']
        output_project_id = config["output_project_id"]
        output_dataset = config["output_dataset"]
        output_table = config.get("output_table")

        tag_project = config["tag_project"]
        tag_dataset = config["tag_dataset"]

        parent = f"projects/{project_id}/locations/{location}"

        if not _info_types:
            _info_types = get_info_types()

        info_types = [
            {"name": info_type} for info_type in _info_types
        ]

        inspect_config = get_inspect_config(info_types, min_likelihood)

        bq_options = get_big_query_storage_options(output_project_id, output_dataset, table_id)

        storage_config = get_storage_config(big_query_options=bq_options)

        save_finding = create_save_finding_action(project_id, table_schema, table_id=output_table)

        inspect_job = {
            "inspect_config": inspect_config,
            "storage_config": storage_config,
            "actions": [save_finding]
        }

        response = create_dlp_job(parent, inspect_job)
        logger.log_text(f"{response}", severity="INFO")

        if next_topic:
            data = {
                "conf_path": conf_path,
                "job_name": response.name,
                "table_project": tag_project,
                "table_schema": tag_dataset,
                "table_id": table_id
            }
            publish_message(project_id, next_topic, data)

        return 'Success', 200

    except Exception as e:
        err = traceback.format_exc()

        logger.log_text(f"Error {err}", severity="ERROR")
        return f"error: {str(e)} ", 200



