
from util.google.storage import get_config
from util.google.pubsub import publish_message, get_message
from util.google.bigquery import query_table
from util.google.datacatalog import get_info_types, get_tag_template, get_entry, apply_column_tags, get_findings
from util.google.dlp import inspect_content

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
        tag_template = config["tag_template"]

        parent = f"projects/{project_id}/locations/{location}"

        if not _info_types:
            _info_types = get_info_types()

        info_types = [
            {"name": info_type} for info_type in _info_types
        ]

        inspect_config = {
            "info_types": info_types,
            "min_likelihood": min_likelihood,
        }

        headers_query = f"SELECT COLUMN_NAME from `{table_project}.{table_schema}.INFORMATION_SCHEMA.COLUMNS` where " \
                        f"TABLE_SCHEMA='{table_schema}' and TABLE_NAME='{table_id}'"

        rows = query_table(headers_query)

        col_names = [row['COLUMN_NAME'] for row in rows]
        headers = [{"name": col} for col in col_names]
        col_list = ','.join(col_names)

        data_query = f"SELECT {col_list} from `{table_project}.{table_schema}.{table_id}`"

        rows = query_table(data_query)


        dlp_rows = []
        for row in rows:
            dlp_rows.append({"values": [{"string_value": str(row[col])} for col in col_names]})

        inspect_item = {
            "table": {
                "headers": headers,
                "rows": dlp_rows
            }

        }

        response = inspect_content(parent, inspect_config, inspect_item)

        summary = get_findings(response)

        # Create a Tag Template.
        tag_template = get_tag_template(project_id, tag_template, info_types)

        entry_name = f"//bigquery.googleapis.com/projects/{table_project}/datasets/{table_schema}/tables/{table_id}"

        entry = get_entry(entry_name)

        apply_column_tags(entry, tag_template, summary)

        if next_topic:
            data = {
                "conf_path": conf_path
            }
            publish_message(project_id, next_topic, data)

        return 'Success', 200

    except Exception as e:
        err = traceback.format_exc()

        logger.log_text(f"Error {err}", severity="ERROR")
        return f"error: {str(e)} ", 200



